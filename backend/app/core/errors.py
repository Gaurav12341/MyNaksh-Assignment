from fastapi import HTTPException


def api_error(status_code: int, code: str, message: str, request_id: str | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": code,
                "message": message,
                "requestId": request_id,
            }
        },
    )
