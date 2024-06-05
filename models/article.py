from sqlalchemy import Column, TEXT, String, DateTime, ForeignKeyConstraint, Boolean
from models.response import ResponseStatusCode, Detail
from sqlalchemy.dialects.postgresql import UUID
from database.conn import DBObject
from typing import Tuple,TypeVar
from datetime import datetime
from .account import Account
from models.base import Base
import traceback
import logging
import uuid

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
        
    @property
    def shallow_info(self):
        return {
            "art_uuid": str(self.art_uuid),
            "a_uuid": str(self.a_uuid),
            "title": self.title,
            "content": self.content,
            'upload_date': self.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
            "is_anonymous": self.is_anonymous
        }


    def __init__(self, a_uuid: str, title: str, content: str, upload_date: datetime, is_anonymous: bool, update_date: datetime = None, category: str = None, art_uuid: str | None = None):
        self.art_uuid = art_uuid
        self.a_uuid = a_uuid
        self.title = title
        self.content = content
        self.upload_date = upload_date
        self.is_anonymous = is_anonymous
        self.update_date = update_date
        self.category = category
    
    @staticmethod
    def insert_article(dbo: DBObject, token: str, title: str, content: str, is_anonymous: bool) -> Tuple[ResponseStatusCode, None | Detail]:
        try:
            response_code, result = Account._decode_token_to_uuid(token)
            if response_code != ResponseStatusCode.SUCCESS:
                return (response_code, result)
            
            article = Article(
                art_uuid=uuid.uuid4(),
                a_uuid=str(result),
                title=title,
                content=content,
                upload_date=datetime.now(),
                is_anonymous=is_anonymous,
            )
            
            dbo.session.add(article)
            dbo.session.commit()
            
            return (ResponseStatusCode.SUCCESS, None)
        
        except Exception as e:
            dbo.session.rollback()
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(f"{e}"))

    @staticmethod
    def delete_article(dbo: DBObject, art_uuid: str, a_uuid: str) -> Tuple[ResponseStatusCode, None | Detail]:
        try:
            article = dbo.session.query(Article).filter_by(art_uuid = art_uuid).first()
            if not article:
                return (ResponseStatusCode.NOT_FOUND, Detail(f"Article with id {art_uuid} not found"))

            if str(article.a_uuid) != a_uuid:
                return (ResponseStatusCode.FAIL, Detail(f"User with id {a_uuid} is not authorized to delete this article"))

            dbo.session.delete(article)
            dbo.session.commit()

            return (ResponseStatusCode.SUCCESS, None)

        except Exception as e:
            dbo.session.rollback()
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    @staticmethod
    def update_article(dbo: DBObject, art_uuid: str, token: str, title: str, content: str, is_anonymous: bool) -> Tuple[ResponseStatusCode, None | Detail]:
        try:
            # Token을 이용하여 사용자 확인
            response_code, result = Account._decode_token_to_uuid(token)
            if response_code != ResponseStatusCode.SUCCESS:
                return (response_code, result)
            
            a_uuid = result
            status_code, result = Article._load_article_from_uuid(dbo, art_uuid)
            if status_code != ResponseStatusCode.SUCCESS:
                return (status_code, result)

            if str(result.a_uuid) != a_uuid:
                return (ResponseStatusCode.FAIL, Detail("User is not authorized to update this article"))

            # 업데이트할 게시물 찾기
            article = dbo.session.query(Article).filter(Article.art_uuid == art_uuid, Article.a_uuid == result.a_uuid).one_or_none()
            if not article:
                return (ResponseStatusCode.NOT_FOUND, Detail(f"Article with id {art_uuid} not found"))

            # 게시물 정보 업데이트
            article.title = title
            article.content = content
            article.is_anonymous = is_anonymous
            article.update_date = datetime.now()

            dbo.session.commit()

            return (ResponseStatusCode.SUCCESS, None)
        
        except Exception as e:
            dbo.session.rollback()
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))
    
    @staticmethod
    def get_article_list(dbo: DBObject, start: int = 0) -> Tuple[ResponseStatusCode, list | Detail]:
        try:
            articles = dbo.session.query(Article).all()
            articles = list(map(lambda x: {    
                "art_uuid": str(x.art_uuid),
                "a_uuid": str(x.a_uuid),
                "title": x.title,
                "content": x.content,
                'upload_date': x.upload_date.strftime("%Y-%m-%d %H:%M:%S"),
                "is_anonymous": x.is_anonymous
            }, articles[start: max(start + 11, len(articles))]))
            return (ResponseStatusCode.SUCCESS, articles)
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))
        
    @staticmethod
    def _load_article_from_uuid(dbo: DBObject, art_uuid: str) -> Tuple[ResponseStatusCode, Article | Detail]:
        try:
            
            article = dbo.session.query(Article).filter_by(art_uuid = art_uuid).first()
            if not article:
                return (ResponseStatusCode.NOT_FOUND, Detail(f"art_uuid {art_uuid} not found in article relation"))
            
            return (ResponseStatusCode.SUCCESS, article)
            
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))