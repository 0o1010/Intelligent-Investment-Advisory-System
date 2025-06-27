from fastapi import status
from fastapi.responses import JSONResponse, Response
from typing import Union


def resp_200(*, data: Union[list, dict, str] = "200 Success", message: str = "Success", total: int = 0) -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': 200,
            'total': total,
            'message': message,
            'data': data,
        }
    )


def resp_400(*, data: str = None, message: str = "400 BAD REQUEST") -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': 400,
            'message': message,
            'data': data,
        }
    )


def resp_401(*, data: str = None, message: str = "401 Unauthorized") -> Response:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            'code': 401,
            'message': message,
            'data': data,
        }
    )


def resp_403(*, data: str = None, message: str = "403 Forbidden") -> Response:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            'code': 403,
            'message': message,
            'data': data,
        }
    )


def resp_404(*, data: str = None, message: str = "404 Not Found") -> Response:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'code': 404,
            'message': message,
            'data': data,
        }
    )


def resp_500(*, data: str = None, message: Union[list, dict, str] = " 500 Server Internal Error") -> Response:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'code': 500,
            'message': message,
            'data': data,
        }
    )
