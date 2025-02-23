from fastapi import Request, HTTPException, Depends, status
from jose import jwt, JWTError
from datetime import datetime

from users.dao import UsersDAO

from users.auth import SECRET_KEY, ALGORITHM

def get_token(request: Request):
    token = request.cookies.get("user_access_token")
    if not token:
        print("Token not")
        return None
    return token


async def get_current_user(token: str):
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
    except JWTError as e:
        print("Token error")
        return None


    expire: str = payload.get("exp")
    if not expire or (int(expire) < datetime.utcnow().timestamp()):
        print("Token expired")
        return None

    user_id: int = payload.get("sub")
    if not user_id:
        print("User id not")
        return None

    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        print("User not")
        return None


    print(f"log {user.name}: {datetime.now()}")
    return user
