from models.response import ResponseStatusCode, ResponseModel
from database.conn import DBObject
from models.article import Article
from models.account import Account
from fastapi import APIRouter, File, UploadFile
from typing import List
import os
import shutil
import uuid

article_router = APIRouter(
    prefix="/article",
    tags=["article"]
)

UPLOAD_DIR = "images/article"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@article_router.get("",
    responses={
        200: {
            "description":"게시물 작성에 성공하여 Article 테이블에 데이터가 등록되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 200, "message": "게시물 작성에 성공하였습니다!"}
                }
            }
        },
        401: {
            "description":"게시물 작성에 실패하여 Article 테이블에 데이터가 등록이 안되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401, "message": "게시물 작성에 실패하였습니다.", "detail": ""}
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
    name = "게시물 조회"
)
async def get_articles(access_token :str, page: int = 1, u_uuid: str | None = None):
    if page < 1:
        return ResponseModel.show_json(ResponseStatusCode.ENTITY_ERROR.value, message = "엔티티 전달이 잘못되었습니다.", detail = "page parameter must be bigger than 0")

    status_code, result = Article.get_article_list(DBObject.instance, access_token, (page - 1) * 10, u_uuid)
    if status_code == ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(ResponseStatusCode.SUCCESS.value, message = "글을 성공적으로 조회했습니다!", articles = result)

    else:
        return ResponseModel.show_json(ResponseStatusCode.INTERNAL_SERVER_ERROR.value, message = "서버 내부 에러가 발생하였습니다", detail = result.text)

@article_router.put("/posting",
    responses={
        200: {
            "description":"게시물 작성에 성공하여 Article 테이블에 데이터가 등록되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 200, "message": "게시물 작성에 성공하였습니다!"}
                }
            }
        },
        401: {
            "description":"게시물 작성에 실패하여 Article 테이블에 데이터가 등록이 안되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401, "message": "게시물 작성에 실패하였습니다.", "detail": ""}
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
async def posting_article(access_token: str, title: str, content: str, is_anonymous: bool, images_files: List[UploadFile] | None = File(None)):
    response_dict = {
        ResponseStatusCode.SUCCESS: "성공적으로 게시물을 적었습니다.",              
        ResponseStatusCode.FAIL: "게시물 작성에 실패하였습니다.",
        ResponseStatusCode.ENTITY_ERROR: "토큰 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 에러가 발생하였습니다."
    }
       
    image_urls = []
    if images_files:
        if len(images_files) > 9:
            return ResponseModel.show_json(ResponseStatusCode.ENTITY_ERROR.value, message="이미지는 최대 9개까지 업로드 가능합니다.", detail="Too many files.")
        
        for file in images_files:
            file_ext = file.filename.split(".")[-1].lower()
            if file_ext not in ["jpeg", "jpg", "png", "gif"]:
                return ResponseModel.show_json(ResponseStatusCode.ENTITY_ERROR.value, message="지원하지 않는 파일 형식입니다.", detail="Unsupported file type.")
            
            file_name = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            image_urls.append(file_path)


    status_code, result = Article.insert_article(DBObject.instance, access_token, title, content, is_anonymous,image_urls=image_urls)

    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code.value, message= response_dict[status_code], Detail= result.text)
        
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code])

@article_router.delete("/delete",
    responses={
        200: {
            "description":"게시물 작성에 성공하여 Article 테이블에 데이터가 등록되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 200, "message": "게시물 작성에 성공하였습니다!"}
                }
            }
        },
        401: {
            "description":"게시물 작성에 실패하여 Article 테이블에 데이터가 등록이 안되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401, "message": "게시물 작성에 실패하였습니다.", "detail": ""}
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
    name = "게시물 삭제"
)
async def delete_article(art_uuid: str, access_token: str):
    response_dict = {
        ResponseStatusCode.SUCCESS: "게시글이 성공적으로 삭제되었습니다.",
        ResponseStatusCode.FAIL: "게시글을 삭제할 권한이 없습니다.",
        ResponseStatusCode.NOT_FOUND: "게시글을 찾을 수 없습니다.",
        ResponseStatusCode.ENTITY_ERROR: "엔티티 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 오류가 발생하였습니다.",
    }
    status_code, result = Account._decode_token_to_uuid(access_token)
    if status_code == ResponseStatusCode.SUCCESS:
        status_code, result = Article.delete_article(DBObject.instance, art_uuid, result)
    
    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code.value, message= response_dict[status_code], Detail= result.text)
        
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code])


@article_router.put("/update",
    responses={
        200: {
            "description":"게시물 수정에 성공하여 Article 테이블에 데이터가 수정되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 200, "message": "게시물 수정에 성공하였습니다!"}
                }
            }
        },
        401: {
            "description":"게시물 수정에 실패하여 Article 테이블에 데이터가 수정이 안되었을 때 발생합니다.",
            "content": {
                "application/json": {
                    "example": {"status_code": 401, "message": "게시물 작성에 실패하였습니다.", "detail": ""}
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
    name = "게시물 수정"
)
async def update_article(art_uuid: str ,access_token: str,  title: str, content: str, is_anonymous: bool):
    response_dict = {
        ResponseStatusCode.SUCCESS: "게시글이 성공적으로 수정되었습니다.",
        ResponseStatusCode.FAIL: "게시글을 수정할 권한이 없습니다.",
        ResponseStatusCode.NOT_FOUND: "게시글을 찾을 수 없습니다.",
        ResponseStatusCode.ENTITY_ERROR: "엔티티 형식이 잘못되었습니다.",
        ResponseStatusCode.INTERNAL_SERVER_ERROR: "서버 내부 오류가 발생하였습니다.",
    }
    
    status_code, result = Article.update_article(DBObject.instance, art_uuid, access_token, title = title, content = content, is_anonymous = is_anonymous)
    
    if status_code != ResponseStatusCode.SUCCESS:
        return ResponseModel.show_json(status_code.value, message= response_dict[status_code], Detail= result.text)
        
    return ResponseModel.show_json(status_code.value, message = response_dict[status_code])

@article_router.get("/image")
async def get_image(image_path: str):
    if os.path.exists(image_path):
        return ResponseModel.show_image(image_path)
    
    else:
        return ResponseModel.show_json(status_code = ResponseStatusCode.NOT_FOUND.value, message = "이미지를 찾을 수 없습니다.")