from datetime import datetime, timedelta
from jose import JWTError, jwt
from argon2 import PasswordHasher, exceptions
from dotenv import load_dotenv
import os
import logging

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

argon2 = PasswordHasher(memory_cost=2**16, parallelism=4, hash_len=32, salt_len=16)

logger = logging.getLogger(__name__)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        argon2.verify(hashed_password, plain_password)
        return True
    except exceptions.VerifyMismatchError:
        logger.debug("Password verification failed: mismatch")
        return False
    except exceptions.InvalidHashError as e:
        logger.error(f"Invalid hash format: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {str(e)}")
        return False


async def get_password_hash(password: str) -> str:
    try:
        return argon2.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    if not data or not JWT_SECRET_KEY:
        raise ValueError("Некорректные данные для создания токена")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": int(expire.timestamp()), "sub": str(data["sub"])})

    jwt_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token


async def verify_token(token: str, credentials_exception) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_id = int(user_id)
        return user_id
    except JWTError as e:
        raise credentials_exception
