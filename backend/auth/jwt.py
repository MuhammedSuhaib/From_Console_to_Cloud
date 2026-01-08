from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")

if not SECRET_KEY:
    raise RuntimeError("BETTER_AUTH_SECRET is missing")

ALGORITHM = "HS256"

def get_current_user_id(creds = Depends(security)) -> str:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise Exception()
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")