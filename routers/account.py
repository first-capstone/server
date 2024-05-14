from models.response import ResponseStatusCode, ResponseModel, Detail
from models.account import SignUpModel, ForgotPasswordModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from database.conn import DBObject
from models.account import Account

session = {}

account_router = APIRouter(
    prefix="/account",
    tags=["account"]
)

@account_router.put("/register", 
    responses={
        200: {
            "description":"회원가입에 성공하여 account 테이블에 데이터가 등록되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 200,"message": "회원가입에 성공하였습니다!"}
                }
            }
        },
        401: {
            "description":"회원가입에 실패하여 account 테이블에 데이터가 등록이 안되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401, "message": "회원가입에 실패하였습니다.", "detail": "regitser is failed."}
                }
            }
        },
        409: {
            "description":"이미 account테이블에 데이터가 등록되어 있을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 409,"message": "이미 등록된 계정 또는 이메일 입니다.","detail": "F_bomber is already exist."}
                }
            }
        },
        422: {
            "description": "데이터 타입 잘못.",
            "content": {
                "application/json":{
                    "example": {"status_code": 422, "message": "데이터 타입 에러","detail": "data type error"}
                }
            } 
        },
        500: {
            "description":"이미 account테이블에 데이터가 등록되어 있을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 500, "message": "서버 내부 에러가 발생하였습니다.", "detail": "Error occured."}
                }
            }
        }
    },
    name = "회원 가입"
)
async def register(model: SignUpModel):
    response_dict = {
        ResponseStatusCode.SUCCESS: "회원가입에 성공하였습니다.",
        ResponseStatusCode.FAIL: "회원가입에 실패하였습니다.",
        ResponseStatusCode.CONFLICT: "이미 등록된 계정 또는 이메일 입니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    status_code, detail = Account.register(DBObject.instance, model.user_id, model.password, model.nickname, model.email, model.phone, model.s_id )

    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code = status_code.value, message = response_dict[status_code], detail = detail.text)
    
    return ResponseModel.show_json(status_code = status_code.value, message = response_dict[status_code])

@account_router.post("/login",
responses={
    200: {
        "description": "로그인 요청이 성공적으로 수행 됐을때 발생한다.",
        "content": {
            "application/json": {
                "example": {"status_code": 200, "message": "로그인에 성공하였습니다.", "token": "access_token here"}
            }
        }
    },
    401: {
        "description": "로그인 요청이 실패 됐을때 발생한다.",
        "content": {
            "application/json": {
                "example": {"status_code": 401,"message": "아이디 또는 비밀번호가 일치하지 않습니다.","detail": "login is false"}
            }
        }
    },
    422:{
        "description": "로그인 요청을 할때 데이터 타입을 잘못 적었을때 발생한다.",
        "content": {
            "application/json": {
                "example": {"status_code": 422, "message": "데이터 타입이 정확하지 않습니다.","detail": "data type error"}
            }
        }
    },
    500:{
        "description": "서버 내부에서 에러가 났을때 발생한다.",
        "content": {
            "application/json": {
                "example": {"status_code": 500, "message": "서버 내부 에러","detail": "Error occured."}
            }
        }
    },
},
name = "로그인"
)
async def login(model: OAuth2PasswordRequestForm = Depends()):
    response_dict = {
        ResponseStatusCode.SUCCESS: "로그인에 성공하였습니다.",
        ResponseStatusCode.FAIL: "아이디 또는 비밀번호가 일치하지 않습니다.",
        ResponseStatusCode.ENTITY_ERROR: "데이터 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    status_code, detail = Account.login(DBObject.instance, model.username, model.password)
    
    if isinstance(detail, Detail):
        return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = detail.text)
        
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code], token = detail.access_token)


@account_router.delete("/signout", 
    responses={
        200: {
            "content": {
                "description": "회원탈퇴 요청이 성공적으로 수행되었을 때 발생합니다.",
                "application/json": {
                    "example": {"status_code": 200,"message": "회원탈퇴에 성공하였습니다."}
                }
            }
        },
        401: {
            "description": "회원탈퇴 요청이 실패했을 때 발생 합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401,"message": "회원탈퇴에 실패하였습니다.", "detail" : "Failed to register_out"}
                }
            }
        },
        408: {
            "description": "세션이 만료 됐을때 뜨는 에러.",
            "content": {
                "application/json": {
                    "example": {"status_code": 408, "message": "세션 만료됨.", "detail": "Session Expiration"}
                }
            }
        }
    },
    name = "회원탈퇴"
)
async def register_out(id: str, password: str):
    response_dict = {
        ResponseStatusCode.SUCCESS: "회원탈퇴에 성공하였습니다.",
        ResponseStatusCode.FAIL: "회원탈퇴에 실패하였습니다.",
        ResponseStatusCode.TIME_OUT: "세션이 만료되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }

    result = (ResponseStatusCode.FAIL, "User Not founded")
    status_code, result = Account._load_user_info(DBObject.instance, id = id)
    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = detail.text)
    
    user = result
    if Account.login(DBObject.instance, id, password)[0] == ResponseStatusCode.SUCCESS:
        result = user.register_out(DBObject.instance)

    status_code, detail = result
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = detail)

@account_router.post("/forgot/password",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "성공적으로 정보를 변경하였습니다."}
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"message": "정보 변경에 실패하였습니다."}
                }
            }
        },
        500: {
            "content": {
                "application/json": {
                    "example": {"message": "서버 내부 에러"}
                }
            }
        }
    },
    name = "비밀번호 변경")
async def forgot_password(model: ForgotPasswordModel):
    response_dict = {
        ResponseStatusCode.SUCCESS: "성공적으로 정보를 변경하였습니다.",              
        ResponseStatusCode.FAIL: "정보 변경에 실패하였습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }

    status_code, result = Account.forgot_password(DBObject.instance, model.user_id, model.password)
    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = result.text)
    
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code])
