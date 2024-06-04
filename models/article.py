from sqlalchemy import Column, TEXT, String, DateTime, ForeignKeyConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from models.response import ResponseStatusCode, Detail
from utility.checker import is_valid_uuid_format
from datetime import datetime,timedelta
from .account import Account
from database.conn import DBObject
from models.base import Base
from typing import Tuple,TypeVar
import traceback
import logging
import uuid
import jwt

Article =TypeVar("Article", bound="Article")

class Article(Base):
    __tablename__ = "article"

    art_uuid: str = Column(UUID(as_uuid=True),
                         primary_key=True, default=uuid.uuid4())  # 게시물 고유 uuid
    a_uuid: str = Column(UUID(as_uuid=True), default=None)  # 계정 고유 uuid
    title: str = Column(String(30), nullable=False) # 게시물 제목
    content : str = Column(TEXT, nullable=False) #게시물 내용
    upload_date: datetime = Column(DateTime, default=datetime.now()) # 게시물 업로드 날짜
    update_date: datetime = Column(DateTime, default=datetime.now()) #게시물 수정 날짜
    category: str = Column(String(20))  # 게시물 카테고리
    is_anonymous : bool = Column(Boolean, default = False) # 게시물 업로드 유저 익명 여부 

    __table_args__ = (ForeignKeyConstraint(
        ["a_uuid"], ["account.a_uuid"],
        ondelete="SET NULL", onupdate="CASCADE"
    ),)

    @property
    def info(self):
        return {
            'art_uuid': str(self.art_uuid),
            'a_uuid': str(self.a_uuid),
            'title': self.title,
            'content': self.content,
            'upload_date': self.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
            'update_date': self.update_date.strftime("%Y-%m-%d %H:%M:%S") if self.update_date else None,
            'category': self.category,
            'is_anonymous': self.is_anonymous
        }


    def __init__(self, art_uuid: str, a_uuid: str, title: str, content: str, upload_date: datetime, is_anonymous: bool, update_date: datetime = None, category: str = None):
        self.art_uuid = art_uuid
        self.a_uuid = a_uuid
        self.title = title
        self.content = content
        self.upload_date = upload_date
        self.is_anonymous = is_anonymous
        self.update_date = update_date
        self.category = category
    
    @staticmethod
    def write_article(dbo: DBObject, token: str, title: str, content: str, is_anonymous: bool):
        # JWT 검증
        response_code, a_uuid_or_detail = Account._decode_token_to_uuid(token)
        if response_code != ResponseStatusCode.SUCCESS:
            return (response_code, a_uuid_or_detail)
        
       # 데이터 타입 검증
        if not isinstance(title, str):
            return (ResponseStatusCode.ENTITY_ERROR, Detail("title is not valid data type, (data type: str)"))
        if not isinstance(content, str):
            return (ResponseStatusCode.ENTITY_ERROR, Detail("content is not valid data type, (data type: str)"))
        if not isinstance(is_anonymous, bool):
            return (ResponseStatusCode.ENTITY_ERROR, Detail("is_anonymous is not valid data type, (data type: bool)"))

        # 새로운 기사 생성
        article = Article(
            art_uuid=uuid.uuid4(),
            a_uuid=str(a_uuid_or_detail),  # 성공 시 a_uuid_or_detail에는 사용자 UUID가 담겨 있음
            title=title,
            content=content,
            upload_date=datetime.now(),
            is_anonymous=is_anonymous,
        )
        try:
            # DB에 저장
            dbo.session.add(article)
            dbo.session.commit()
            # 성공 메시지 반환
            return (ResponseStatusCode.SUCCESS, None)
        except Exception as e:
            # 예외 발생 시 DB 롤백 및 에러 메시지 반환
            dbo.session.rollback()
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(f"{e}"))

    @staticmethod
    def delete_article(dbo: DBObject, art_uuid: str, a_uuid: str) -> Tuple[ResponseStatusCode, Detail]:
        """Deletes an article from the database.

        Args:
            dbo (DBObject): Database connection object.
            art_uuid (str): Unique identifier of the article to delete.
            a_uuid (str): Unique identifier of the user who wants to delete the article.

        Returns:
            Tuple[ResponseStatusCode, Detail]: 
                - ResponseStatusCode: Indicates the result of the operation (SUCCESS or error code).
                - Detail: Additional details about the response (None for success, error message otherwise).
        """

        try:
            # Check if the article exists
            article = dbo.session.query(Article).filter_by(art_uuid=art_uuid).first()
            if not article:
                return (ResponseStatusCode.ENTITY_NOT_FOUND, Detail(f"Article with id {art_uuid} not found"))

            # Check if the user has permission to delete the article (ownership check)
            if article.a_uuid != a_uuid:
                return (ResponseStatusCode.UNAUTHORIZED, Detail(f"User with id {a_uuid} is not authorized to delete this article"))

            # Delete the article from the database
            dbo.session.delete(article)
            dbo.session.commit()

            # Success message
            return (ResponseStatusCode.SUCCESS, None)

        except Exception as e:
            # Error handling
            dbo.session.rollback()
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))
        
