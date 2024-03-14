from fastapi.responses import JSONResponse
from fastapi import FastAPI
import uvicorn

from database.conn import DBObject

dbObj = DBObject()
app = FastAPI()


@app.get("/")
def index():
    return JSONResponse({"message": "Hello World"})


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
