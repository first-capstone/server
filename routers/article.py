from fastapi import APIRouter, Depends
from typing import Union
#id,pwd:F_bomber
#여긴 임시#
from database.conn import DBObject
from models.response import ResponseStatusCode, ResponseModel, Detail
from models.article import Article



article_router = APIRouter(
    prefix="/article",
    tags=["article"]
)



@article_router.put("/posting",
    responses={
        200: {
            "description":"게시물 작성에 성공하여 Article 테이블에 데이터가 등록되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 200,"message": "게시물 작성에 성공하였습니다!"}
                }
            }
        },
        401: {
            "description":"게시물 작성에 실패하여 Article 테이블에 데이터가 등록이 안되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401, "message": "게시물 작성에 실패하였습니다.", "detail": "regitser is failed."}
                }
            }
        },
        422: {
            "description": "데이터 길이가 너무 길면 발생합니다.",
            "content": {
                "application/json":{
                    "example": {"status_code": 422, "message": "데이터 길이 에러","detail": "data type error"}
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
    name = "게시물 작성"
)
async def write_article(token: str, title: str, content: str, is_anonymous: bool):
    response_dict = {
        ResponseStatusCode.SUCCESS: "성공적으로 게시물을 적었습니다.",              
        ResponseStatusCode.FAIL: "게시물 작성에 실패하였습니다.",
        ResponseStatusCode.ENTITY_ERROR: "입력 데이터 타입이 잘못됨",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }

    status_code, detail = Article.write_article(DBObject.instance, token, title, content, is_anonymous)

    if isinstance(detail, Detail):
        return ResponseModel.show_json(status_code.value, message= response_dict[status_code], Detail= detail.text)
        
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code])
    