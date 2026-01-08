import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
import os

logger = logging.getLogger(__name__)

security = HTTPBearer()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")

if not SECRET_KEY:
    raise RuntimeError("BETTER_AUTH_SECRET is missing")

ALGORITHM = "HS256"

def get_current_user_id(creds = Depends(security)) -> str:
    logger.info(f"Verifying JWT token: {creds.credentials[:20]}..." if creds.credentials else "No credentials provided")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"JWT decoded successfully, payload keys: {list(payload.keys())}")

        user_id = payload.get("sub")
        logger.info(f"Extracted user_id from 'sub': {user_id}")

        if not isinstance(user_id, str):
            logger.error(f"user_id is not a string: {type(user_id)}, value: {user_id}")
            raise Exception("Invalid user_id type")

        logger.info(f"Returning user_id: {user_id}")
        return user_id
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"General error in JWT verification: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")