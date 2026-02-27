from fastapi import Query, HTTPException, Depends
from src.core.jwt import decode_jwt_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError


class Pagination:
    def __init__(
        self, page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100)
    ):
        self.page = page
        self.limit = limit


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )

    return int(user_id)


def verify_user_access(user_id_jwt: int = Depends(get_current_user_id)):
    if not user_id_jwt:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id_jwt


def dev_verify_user(user_id: int, user_id_jwt: int = Depends(get_current_user_id)) -> int:
    if user_id != user_id_jwt:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user_id