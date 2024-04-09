from models.response import ResponseStatusCode, ResponseModel, Detail
from models.university import University
from database.conn import DBObject
from fastapi import APIRouter

univ_router = APIRouter(
    prefix="/univ",
    tags=["univ"]
)

@univ_router.get("/", responses={
    200: {
        "description": "u_uuid에 삽입되어 있는 값은, 실제 존재하지 않는 값입니다.",
        "content": {
            "application/json": {
                "example": {
                    "status_code": 200, "message": "데이터를 불러오는데 성공하였습니다.", "univ_list": [
                        {
                            "u_uuid": "066ce1a1-4153-4b3e-9a3a-04b92a877fc1",
                            "univ_name": "서울대학교"
                        },
                        {
                            "u_uuid": "ff934e6f-294b-472a-8e64-6e1c3b012a1b",
                            "univ_name": "고려대학교"
                        },
                        {
                            "u_uuid": "4013a665-b7c5-45a5-9bb4-c31576820151",
                            "univ_name": "연세대학교"
                        },
                        {
                            "u_uuid": "f50f071e-06e1-43f5-aae3-dfb8c23fb063",
                            "univ_name": "배재대학교"
                        },
                        {
                            "u_uuid": "290b7568-1800-4e07-a628-3f74061de2df",
                            "univ_name": "우송대학교"
                        },
                        {
                            "u_uuid": "9ab8c8f9-98f6-4681-92bf-411982a7651d",
                            "univ_name": "목원대학교"
                        }
                    ]
                }
            }
        }
    },
    404: {
        "description": "데이터베이스에 데이터가 존재하지 않을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 404, "message": "데이터를 불러오는데 실패하였습니다", "detail": "Data doesn't exist"}
            }
        }
    },
    500: {
        "description": "예상하지 못한 서버 에러가 발생하였을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 500, "message": "서버 내부 에러가 발생하였습니다.", "detail": "Error occured"}
            }
        }
    }
}, 
name="대학교 이름 조회",
description = "데이터베이스 내부에 존재하는 모든 대학교의 이름, uuid를 조회합니다.")
async def get_all_univ_list():
    message_dict = {
        ResponseStatusCode.SUCCESS: "데이터를 불러오는데 성공하였습니다.",
        ResponseStatusCode.NOT_FOUND: "데이터를 불러오는데 실패하였습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }

    status_code, result = University.get_univ_name_list(DBObject.instance)
    if isinstance(result, Detail):
        return ResponseModel.show_json(status_code=status_code.value, message = message_dict[status_code], detail = result.text)
        
    return ResponseModel.show_json(status_code = status_code.value, message = message_dict[status_code], univ_list = result)

@univ_router.get("/search", responses={
    200: {
        "description": "u_uuid에 삽입되어 있는 값은, 실제 존재하지 않는 값입니다.",
        "content": {
            "application/json": {
                "example": {
                    "status_code": 200, "message": "데이터를 불러오는데 성공하였습니다.", "univ_list": [
                        {
                            "u_uuid": "066ce1a1-4153-4b3e-9a3a-04b92a877fc1",
                            "univ_name": "서울대학교"
                        },
                        {
                            "u_uuid": "ff934e6f-294b-472a-8e64-6e1c3b012a1b",
                            "univ_name": "고려대학교"
                        },
                        {
                            "u_uuid": "4013a665-b7c5-45a5-9bb4-c31576820151",
                            "univ_name": "연세대학교"
                        },
                        {
                            "u_uuid": "f50f071e-06e1-43f5-aae3-dfb8c23fb063",
                            "univ_name": "배재대학교"
                        },
                        {
                            "u_uuid": "290b7568-1800-4e07-a628-3f74061de2df",
                            "univ_name": "우송대학교"
                        },
                        {
                            "u_uuid": "9ab8c8f9-98f6-4681-92bf-411982a7651d",
                            "univ_name": "목원대학교"
                        }
                    ]
                }
            }
        }
    },
    404: {
        "description": "데이터베이스에 데이터가 존재하지 않을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 404, "message": "데이터를 불러오는데 실패하였습니다", "detail": "Data doesn't exist"}
            }
        }
    },
    422: {
        "description": "search값이 제대로 전달되지 않았을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code":422, "message":"Validation 오류가 발생하였습니다", "detail":"missing in query/search, Field required"}
            }
        }
    },
    500: {
        "description": "예상하지 못한 서버 에러가 발생하였을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 500, "message": "서버 내부 에러가 발생하였습니다.", "detail": "Error occured"}
            }
        }
    }
}, 
name="대학교 이름 조회",
description = "데이터베이스 내부에 존재하는 모든 대학교의 이름, uuid를 조회합니다.")
async def search_univ_list(search: str, skip: int = 0 , count: int = 10):
    message_dict = {
        ResponseStatusCode.SUCCESS: "데이터를 불러오는데 성공하였습니다.",
        ResponseStatusCode.NOT_FOUND: "데이터를 불러오는데 실패하였습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }

    status_code, result = University.search_univ_name(DBObject.instance, search, count, skip)
    if isinstance(result, Detail):
        return ResponseModel.show_json(status_code=status_code.value, message = message_dict[status_code], detail = result.text)
        
    return ResponseModel.show_json(status_code = status_code.value, message = message_dict[status_code], univ_list = result)

@univ_router.get("/desc/{u_uuid}", responses={
    200: {
        "description": "배재대학교 데이터 샘플입니다.",
        "content": {
            "application/json": {
                "example": { "status_code": 200, "message": "데이터를 불러오는데 성공하였습니다.", "univ_info": {
                    "u_uuid": "9b946366-16a7-4fec-9485-341fb64872f7",
                    "est_type": "사립",
                    "univ_gubun": "대학(4년제)",
                    "address": "대전광역시 서구 배재로 155-40 (도마동, 배재대학교)",
                    "link": "http://www.pcu.ac.kr",
                    "logo_path": "./images/logos/배재대학교.png",
                    }
                }
            }
        }
    },
    404: {
        "description": "uuid값을 가지고 있는 튜플이 데이터베이스에 존재하지 않을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 404, "message": "데이터를 찾는데 실패하였습니다.", "detail": "0939c83e-b5e7-4fd1-b3b1-0babe272ebbb not founded in university"}
            }
        }
    },
    422: {
        "description": "uuid 포맷이 맞지 않을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 422, "message": "입력 형식이 잘못되었습니다.", "detail": "test-uuid-format-wow is not valid uuid format"}
            }
        }
    },
    500: {
        "description": "예상하지 못한 서버 에러가 발생하였을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 500, "message": "서버 내부 에러가 발생하였습니다.", "detail": "Error occured"}
            }
        }
    }
},
name="대학교 정보 자세히 조회",
description="데이터베이스에서 입력받은 u_uuid 값을 가지고 있는 university 튜플을 조회합니다.")
async def get_univ_desc(u_uuid: str):
    message_dict = {
        ResponseStatusCode.SUCCESS: "데이터를 불러오는데 성공하였습니다.",
        ResponseStatusCode.NOT_FOUND: "데이터를 찾는데 실패하였습니다.",
        ResponseStatusCode.ENTITY_ERROR: "입력 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }

    status_code, result = University.get_univ_from_uuid(DBObject.instance, u_uuid)
    if isinstance(result, Detail):
        return ResponseModel.show_json(status_code = status_code.value, message = message_dict[status_code], detail = result.text)
    
    return ResponseModel.show_json(status_code = status_code.value, message = message_dict[status_code], univ_info = result.info)

@univ_router.get("/logo/{u_uuid}", responses = {
    200: {
        "description": f"<img src='https://i.namu.wiki/i/eEKFz5UCJYqutAgfCeNFzCQ2w9mC8OAgzj4lpQbmdousRWrY-9dvzEgParxEgw1sFIoNACBLSw3_No-TLokfuw.svg' width='200px' height='200px'/>",
        "content": None
    },
    404: {
        "description": "uuid값을 가지고 있는 튜플이 데이터베이스에 존재하지 않을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 404, "message": "데이터를 찾는데 실패하였습니다.", "detail": "0939c83e-b5e7-4fd1-b3b1-0babe272ebbb not founded in university"}
            }
        }
    },
    422: {
        "description": "uuid 포맷이 맞지 않을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 422, "message": "입력 형식이 잘못되었습니다.", "detail": "test-uuid-format-wow is not valid uuid format"}
            }
        }
    },
    500: {
        "description": "예상하지 못한 서버 에러가 발생하였을 때 발생합니다.",
        "content": {
            "application/json": {
                "example": {"status_code": 500, "message": "서버 내부 에러가 발생하였습니다.", "detail": "Error occured"}
            }
        }
    }
}, 
name="대학교 로고 불러오기",
description="데이터베이스에서 입력받은 u_uuid 값을 가지고 있는 university logo 조회합니다.")
async def get_univ_logo(u_uuid):
    message_dict = {
        ResponseStatusCode.SUCCESS: "데이터를 불러오는데 성공하였습니다.",
        ResponseStatusCode.NOT_FOUND: "데이터를 찾는데 실패하였습니다.",
        ResponseStatusCode.ENTITY_ERROR: "입력 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    status_code, result = University.get_univ_from_uuid(DBObject.instance, u_uuid)
    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code = status_code.value, message = message_dict[status_code], detail = result.text)
    
    university = result
    status_code, logo_path = university.get_logo_path()
    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code = status_code.value, message = message_dict[status_code], detail = result.text)
        
    return ResponseModel.show_image(logo_path)