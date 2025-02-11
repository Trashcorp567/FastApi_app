import secrets
import uuid
from time import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_auth_basic(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    return {
        "message": "hi",
        "username": credentials.username,
        "passwords": credentials.password,
    }


usernames_to_pass = {
    "admin": "admin",
    "vlad": "password"
}


static_auth_token_to_username = {
    "a021030415asdf230": "admin",
    "da1231454323241234": "Vlad"
}


def get_username_by_static_auth_token(
        auth_token: str = Header(alias="x-auth-token")
) -> str:
    if username := static_auth_token_to_username.get(auth_token):
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid Token",
    )


def get_auth_user_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid user or pass",
        headers={"WWW_Authenticate": "Basic"},
    )
    correct_pass = usernames_to_pass.get(credentials.password)
    if correct_pass is None:
        raise unauthed_exc

    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_pass.encode("utf-8"),
    ):
        raise unauthed_exc

    return credentials.username


@router.get("/basic-auth-username/")
def demo_auth_basic_username(
        auth_username: str = Depends(get_auth_user_username)
):
    return {
        "message": f"hi {auth_username}",
        "username": auth_username,
    }


@router.get("/some-http-header-basic-auth/")
def demo_auth_http_header(
    username: str = Depends(get_username_by_static_auth_token)
):
    return {
        "message": f"hi! {username}",
        "username": username,
    }


COOKIES: dict[str, dict[str, Any]] = {}
COOKIES_KEY = "web_app_cookie"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def get_session_data(
    session_id: str = Cookie(alias=COOKIES_KEY)
):
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )
    return COOKIES[session_id]


@router.post("/login-cookie/")
def demo_auth_cookie_login_header(
    response: Response,
    username: str = Depends(get_auth_user_username),
):
    session_id = generate_session_id()
    COOKIES[session_id] = {
        "username": username,
        "time": int(time()),
    }
    response.set_cookie(COOKIES_KEY, session_id)
    return {
        "result": "ok",
    }


@router.get("/check_cookie")
def demo_auth_by_cookie(
        user_session_data: dict = Depends(get_session_data)
):
    username = user_session_data["username"]
    return {
        "message": f"Hello {username}!",
        **user_session_data
    }


@router.get("/logout_cookie")
def demo_auth_by_cookie_logout(
    response: Response,
    session_id: str = Cookie(alias=COOKIES_KEY),
    user_session_data: dict = Depends(get_session_data)
):
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIES_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye {username}!",
    }
