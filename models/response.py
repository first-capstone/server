from enum import Enum
from fastapi.responses import JSONResponse

class ResponseStatusCode(Enum):
    SUCCESS = 200  # 성공
    FAIL = 401  # 실패
    FORBIDDEN = 403  # 접근 권한 없음
    NOT_FOUND = 404  # 경로 또는 자료를 찾을 수 없음 (보통 경로)
    TIME_OUT = 408  # 세션 만료됨
    CONFLICT = 409  # 데이터 충돌
    ENTITY_ERROR = 422  # 입력 데이터 타입이 잘못됨
    INTERNAL_SERVER_ERROR = 500  # 서버 내부 에러

class ResponseModel(Enum):
    status_code: int
    message: str | None = None
    detail: str | None = None
    
    @staticmethod
    def show_json(status_code: int, message: str | None = None, detail: str | None = None):
        show_dict = {"status_code": status_code}
        if message:
            show_dict["message"] = message
            
        if detail:
            show_dict["detail"] = detail
            
        return JSONResponse(show_dict, status_code = status_code)