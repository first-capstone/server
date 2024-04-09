from models.response import ResponseModel, ResponseStatusCode
from fastapi.exceptions import RequestValidationError
from env.UNIVERSITY import CARRERNET_URL, API_KEY
from database.conn import DBObject
from models import University
from fastapi import FastAPI
import uvicorn
import routers


app = FastAPI()
app.include_router(routers.univ_router)
app.include_router(routers.account_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    data = exc.__dict__["_errors"][0]
    message = "데이터를 서버에 전송해 주세요." if data["type"] == "missing" else "Validation 오류가 발생하였습니다."
    print(data)
    return ResponseModel.show_json(
        status_code=422,
        message=message,
        detail=f"{data['type']} {data['loc'][0]} in {data['loc'][1]}, {data['msg']}"
    )

if __name__ == "__main__":
    status_code, data = University._check_data_exist(DBObject.instance)
    if status_code != ResponseStatusCode.CONFLICT:
        status_code, result = University._init_univ(DBObject.instance, CARRERNET_URL, API_KEY)
        if status_code != ResponseStatusCode.SUCCESS:
            print(result.text)
            exit(0)
    
    status_code, data = University._check_image_exist(DBObject.instance)
    
    uvicorn.run("main:app", reload=True, host = "0.0.0.0", port = 8080)
