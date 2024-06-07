from models.response import ResponseStatusCode, Detail
from typing import Dict, Any, List, TypeVar, Tuple
from utility.checker import is_valid_uuid_format
from sqlalchemy import Column, String, TEXT, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from database.conn import DBObject
from models.base import Base
from pathlib import Path
from PIL import Image
import traceback
import requests
import logging
import rembg
import uuid
import os

University = TypeVar("University", bound="University")

class UniversityNameModel:
    u_uuid: str
    univ_name: str
    address: str

    def __init__(self, row: Row):
        self.u_uuid = row.u_uuid
        self.univ_name = row.univ_name
        self.address = row.address

    @property
    def info(self):
        return {"u_uuid": str(self.u_uuid),
                "univ_name": f"{self.univ_name}({self.address.split(' ')[0]})"}


class University(Base):
    __tablename__ = "university"

    u_uuid = Column(UUID(as_uuid=True), nullable=False,
                    default=uuid.uuid4, primary_key=True)
    univ_name = Column(String(30), nullable=False)
    link = Column(TEXT, nullable=True, default=None)
    est_type = Column(String(2), nullable=False)
    univ_gubun = Column(String(10), nullable=False)
    address = Column(TEXT, nullable=False)
    logo_path = Column(TEXT, nullable=True, default=None)

    def __init__(
        self,
        univ_name,
        est_type,
        univ_gubun,
        address,
        logo_path=None,
        link=None,
        u_uuid=None
    ):
        self.univ_name = univ_name
        self.est_type = est_type
        self.univ_gubun = univ_gubun
        self.address = address
        self.logo_path = logo_path
        self.link = link
        self.u_uuid = u_uuid

    @property
    def info(self):
        return {
            "univ_name": self.univ_name,
            "est_type": self.est_type,
            "univ_gubun": self.univ_gubun,
            "address": self.address,
            "link": self.link,
            "logo_path": self.logo_path,
            "u_uuid": str(self.u_uuid)
        }

    @staticmethod
    def get_univ_name_list(
        dbo: DBObject
    ) -> Tuple[ResponseStatusCode, List[UniversityNameModel] | Detail]:
        try:
            data = dbo.session.query(University.u_uuid,
                                    University.address,
                                    University.univ_name).all()

            if len(data) == 0:
                return (ResponseStatusCode.NOT_FOUND,
                        Detail("Data doesn't exist"))

            return (ResponseStatusCode.SUCCESS,
                    list(map(lambda x: UniversityNameModel(x).info, data)))

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    @staticmethod
    def get_univ_from_uuid(
        dbo: DBObject,
        u_uuid: str
    ) -> Tuple[ResponseStatusCode, University | Detail]:
        try:
            if not is_valid_uuid_format(u_uuid):
                return (ResponseStatusCode.ENTITY_ERROR,
                        Detail(f"{u_uuid} is not valid uuid format"))

            university = dbo.session.query(University)\
                .filter_by(u_uuid=u_uuid).first()
            if university:
                return (ResponseStatusCode.SUCCESS, university)

            else:
                return (ResponseStatusCode.NOT_FOUND,
                        Detail(f"{u_uuid} not founded in university"))

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    def get_logo_path(self) -> Tuple[ResponseStatusCode, str | Detail]:
        try:
            if self.logo_path is None:
                self.logo_path = f"./images/logos/\
                    {self.univ_name.split(' ')[0]}.png"

            return (ResponseStatusCode.SUCCESS, self.logo_path)

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))
        
    @staticmethod
    def _load_all_u_uuid(dbo: DBObject) -> Tuple[ResponseStatusCode, list | Detail]:
        try:
            results = dbo.session.query(University.u_uuid).all()
            return (ResponseStatusCode.SUCCESS, list(map(lambda x: str(x[0]), results)))
            
        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    @staticmethod
    def _change_logo_extension() -> Tuple[ResponseStatusCode, None | str]:
        try:
            LOGO_ROOT_PATH = "./images/logos"
            for img_path in os.listdir(LOGO_ROOT_PATH):
                path_obj = Path(f"{LOGO_ROOT_PATH}/{img_path}")
                path_obj.rename(path_obj.with_suffix(".png"))

            return (ResponseStatusCode, None)

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    @staticmethod
    def _remove_icon_background() -> Tuple[ResponseStatusCode, None | str]:
        try:
            LOGO_ROOT_PATH = "./images/logos"
            for img_path in os.listdir(LOGO_ROOT_PATH):
                img = Image.open(f"{LOGO_ROOT_PATH}/{img_path}")
                out = rembg.remove(img)
                out.save(f"{LOGO_ROOT_PATH}/{img_path}")

            return (ResponseStatusCode, None)

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    @staticmethod
    def _check_image_exist(
        dbo: DBObject
    ) -> Tuple[ResponseStatusCode, None | Detail]:
        try:
            LOGO_ROOT_PATH = "./images/logos"
            data = dbo.session.query(University.univ_name).all()[0]

            for univ_name in data:
                if not os.path.exists(f"{LOGO_ROOT_PATH}/{univ_name}.png"):
                    return (ResponseStatusCode.NOT_FOUND,
                            Detail(str(f"University's logo doesn't exist in \
                                {LOGO_ROOT_PATH}/{univ_name}.png")))

            return (ResponseStatusCode.SUCCESS, None)

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

    @staticmethod
    def _resize_logo() -> Tuple[ResponseStatusCode, None | Detail]:
        LOGO_ROOT_PATH = "./images/logos"
        for img_path in os.listdir(LOGO_ROOT_PATH):
            img = Image.open(f"{LOGO_ROOT_PATH}/{img_path}")
            img = img.resize((200, 200))
            img.save(f"{LOGO_ROOT_PATH}/{img_path}")

    @staticmethod
    def _check_data_exist(
        dbo: DBObject
    ) -> Tuple[ResponseStatusCode, None | str]:
        return {
            True: (ResponseStatusCode.SUCCESS, None),
            False: (ResponseStatusCode.CONFLICT,
                    Detail("Data Conflicted in University._check_data_exist"))
        }[dbo.session.query(University).all() == []]

    @staticmethod
    def _crawl_univ_info(
        URL: str,
        API_KEY: str
    ) -> Tuple[ResponseStatusCode, List[Dict[str, Any]] | str]:
        try:
            params = {"apiKey": API_KEY, "svcType": "api",
                    "svcCode": "SCHOOL", "contentType": "json",
                    "gubun": "univ_list", "perPage": 500}

            response = requests.get(URL, params=params)

            if response.status_code == 200:
                data = response.json()
                return (ResponseStatusCode.SUCCESS,
                        list(map(lambda x: {"univ_name": x["schoolName"],
                                            "univ_gubun": x["schoolGubun"],
                                            "address": x["adres"],
                                            "link": x["link"],
                                            "est_type": x["estType"],
                                            "total": x["totalCount"]},
                                data["dataSearch"]["content"])))

            else:
                return (ResponseStatusCode.FAIL,
                        Detail("""URL Not Responded in \
                            University._crawl_univ_info"""))

        except requests.exceptions.ConnectionError:
            return (ResponseStatusCode.NOT_FOUND,
                    Detail("URL Not Found in University._crawl_univ_info"))

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, str(e))

    @staticmethod
    def _insert_univ_info(
        dbo: DBObject,
        univ_info: List[Dict[str, Any]]
    ) -> Tuple[ResponseStatusCode, str | None]:
        try:
            for u in univ_info:
                univ = University(
                    univ_name=u["univ_name"],
                    est_type=u["est_type"],
                    link=u["link"],
                    address=u["address"],
                    univ_gubun=u["univ_gubun"]
                )
                dbo.session.add(univ)

            return (ResponseStatusCode.SUCCESS, None)

        except IntegrityError:
            return (ResponseStatusCode.CONFLICT,
                    Detail("""Data Already Exist in
                        University._insert_univ_info"""))

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))

        finally:
            dbo.session.commit()

    @staticmethod
    def _init_univ(
        dbo: DBObject,
        URL: str,
        API_KEY: str
    ) -> Tuple[ResponseStatusCode, str | None]:
        try:
            result, data = University._check_data_exist(dbo)
            if result != ResponseStatusCode.SUCCESS:
                return (result, data)

            result, data = University._crawl_univ_info(URL, API_KEY)
            if result != ResponseStatusCode.SUCCESS:
                return (result, data)

            if int(data[0]["total"]) != len(data):
                return (ResponseStatusCode.DATA_REQUIRED,
                        Detail("""Total University Count Not Equals in
                            University._init_univ"""))

            else:
                result, detail = University._insert_univ_info(dbo, data)
                if isinstance(detail, Detail):
                    raise Exception(detail.message)

                return (ResponseStatusCode.SUCCESS, None)

        except Exception as e:
            logging.error(f"""{e}: {''.join(traceback.format_exception(None,
                        e, e.__traceback__))}""")
            return (ResponseStatusCode.INTERNAL_SERVER_ERROR, Detail(str(e)))
