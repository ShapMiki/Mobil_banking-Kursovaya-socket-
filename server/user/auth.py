from passlib.context import CryptContext
from datetime import datetime, timedelta

from jose import JWTError, jwt

from pydantic import EmailStr


from user.dao import UsersDAO

from config import settings



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

####Вынести в enx
SECRET_KEY = settings.secret_key_for_jwt # "b3e7b3b3e7b3b3e7"
ALGORITHM = settings.algorithm_for_jwt



def get_current_user(request):
    token = request['headers']['JWT']
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

    user = UsersDAO.find_by_id(int(user_id))

    if not user:
        print("User not")
        return None


    print(f"log {user.name}: {datetime.utcnow()}")
    return user


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def get_password_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Error hashing password: {e}")
        raise


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24*7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(telephone:str, password: str):
    try:
        user = UsersDAO.find_one_or_none(telephone=telephone)
        if not user or not verify_password(password, user.password):
            return None
        return user
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None