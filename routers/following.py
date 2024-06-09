from models.response import ResponseStatusCode, ResponseModel
from models.following import Following
from models.account import Account
from database.conn import DBObject
from fastapi import APIRouter

following_router = APIRouter(
    prefix="/account",
    tags=["account"]
)

@following_router.post("/follow")
async def follow(access_token: str, u_uuid: str):
    response_dict = {
        ResponseStatusCode.SUCCESS: "팔로우에 성공하였습니다!",
        ResponseStatusCode.ENTITY_ERROR: "토큰 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    status_code, result = Account._decode_token_to_uuid(access_token)
    if status_code == ResponseStatusCode.SUCCESS:
        status_code, result = Following.follow(DBObject.instance, a_uuid = result, u_uuid = u_uuid)
        if status_code == ResponseStatusCode.SUCCESS:
            return ResponseModel.show_json(status_code. value, message = response_dict[status_code])
    
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = result.text)

@following_router.post("/unfollow")
async def unfollow(access_token: str, u_uuid: str):
    response_dict = {
        ResponseStatusCode.SUCCESS: "팔로우에 성공하였습니다!",
        ResponseStatusCode.ENTITY_ERROR: "토큰 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    status_code, result = Account._decode_token_to_uuid(access_token)
    if status_code == ResponseStatusCode.SUCCESS:
        status_code, result = Following.unfollow(DBObject.instance, result, u_uuid)
        if status_code == ResponseStatusCode.SUCCESS:
            return ResponseModel.show_json(status_code. value, message = response_dict[status_code])
    
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = result.text)

@following_router.get("/follow/list")
async def follow_list(access_token: str):
    response_dict = {
        ResponseStatusCode.SUCCESS: "성공적으로 조회하였습니다.",
        ResponseStatusCode.ENTITY_ERROR: "토큰 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
    
    status_code, result = Account._decode_token_to_uuid(access_token)
    if status_code == ResponseStatusCode.SUCCESS:
        status_code, result = Following.get_follow_univ_list(DBObject.instance, result)
        if status_code == ResponseStatusCode.SUCCESS:
            return ResponseModel.show_json(status_code. value, message = response_dict[status_code], univ_list = result)
    
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code], detail = result.text)