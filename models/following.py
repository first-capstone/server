from sqlalchemy import Column, DateTime, ForeignKeyConstraint
from models.response import ResponseStatusCode, Detail
from utility.checker import is_valid_uuid_format
from sqlalchemy.dialects.postgresql import UUID
from models.university import University
from database.conn import DBObject
from models.account import Account
from datetime import datetime
from models.base import Base
from typing import Tuple, TypeVar
import traceback
import logging
import uuid

Following = TypeVar("Following", bound="Following")

class Following(Base):
    __tablename__ = "following"
    
    f_uuid = Column(UUID(as_uuid=True),
                         primary_key=True, default=uuid.uuid4()) 
    a_uuid = Column(UUID(as_uuid = True), default = None)
    u_uuid = Column(UUID(as_uuid = True), default = None)
    following_date = Column(DateTime, default = datetime.now())
    
    __table_args__ = (ForeignKeyConstraint(
        ["u_uuid"], ["university.u_uuid"]
    ),ForeignKeyConstraint(
        ["a_uuid"], ["account.a_uuid"]
        ),
    )
    
    def __init__(self, a_uuid: str, u_uuid: str):
        self.a_uuid = a_uuid
        self.u_uuid = u_uuid
        
    @staticmethod
    def follow(dbo: DBObject, a_uuid: str, u_uuid: str) -> Tuple[ResponseStatusCode, None | Detail]:
        try:
            if not is_valid_uuid_format(a_uuid):
                return (ResponseStatusCode.ENTITY_ERROR, Detail(f"a_uuid {a_uuid} is not match format"))
            
            if not is_valid_uuid_format(u_uuid):
                return (ResponseStatusCode.ENTITY_ERROR, Detail(f"u_uuid {u_uuid} is not match format"))

            status_code, result = Account._load_user_info(dbo, a_uuid = a_uuid)
            if status_code != ResponseStatusCode.SUCCESS:
                return (status_code, result)
            
            status_code, result = University._load_all_u_uuid(dbo)
            if status_code != ResponseStatusCode.SUCCESS:
                return (status_code, result)
            
            if u_uuid not in result:
                return (ResponseStatusCode.NOT_FOUND, Detail(f"u_uuid {u_uuid} not in University relation"))
            
            follow_obj = Following(a_uuid, u_uuid)
            dbo.session.add(follow_obj)
            dbo.session.commit()
            return (ResponseStatusCode.SUCCESS, None)
            
        except Exception as e:
            dbo.session.rollback()
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(f"{e}"))
        
    @staticmethod
    def unfollow(dbo: DBObject, a_uuid: str, u_uuid: str) -> Tuple[ResponseStatusCode, None | Detail]:
        try:
            if not is_valid_uuid_format(a_uuid):
                return (ResponseStatusCode.ENTITY_ERROR, Detail(f"a_uuid {a_uuid} is not match format"))
            
            if not is_valid_uuid_format(u_uuid):
                return (ResponseStatusCode.ENTITY_ERROR, Detail(f"u_uuid {u_uuid} is not match format"))
            
            status_code, result = Account._load_user_info(dbo, a_uuid = a_uuid)
            if status_code != ResponseStatusCode.SUCCESS:
                return (status_code, result)
            
            status_code, result = University._load_all_u_uuid(dbo)
            if status_code != ResponseStatusCode.SUCCESS:
                return (status_code, result)
            
            if u_uuid not in result:
                return (ResponseStatusCode.NOT_FOUND, Detail(f"u_uuid {u_uuid} not in University relation"))
            
            follow_obj = Following(a_uuid, u_uuid)
            dbo.session.delete(follow_obj)
            dbo.session.commit()
            return (ResponseStatusCode.SUCCESS, None)
            
        except Exception as e:
            dbo.session.rollback()
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(f"{e}"))
    
    @staticmethod
    def get_follow_univ_list(dbo: DBObject, a_uuid: str):
        try:
            results = dbo.session.query(Following.u_uuid).filter_by(a_uuid = a_uuid).all()
            return (ResponseStatusCode.SUCCESS, list(map(lambda x: str(x[0]), results)))
        
        except Exception as e:
            logging.error(f"{e}: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(f"{e}"))