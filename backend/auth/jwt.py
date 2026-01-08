import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
import os
import requests

logger = logging.getLogger(__name__)

security = HTTPBearer()

# This is where Next.js is running
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

def get_current_user_id(creds = Depends(security)) -> str:
    token = creds.credentials
    try:
        # 1. Get the Key ID (kid) from the token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        # 2. Fetch the public keys from the Next.js auth server
        # In a real app, you would cache this so it's not slow!
        jwks_url = f"{BETTER_AUTH_URL}/api/auth/.well-known/jwks.json"
        res = requests.get(jwks_url)
        jwks = res.json()

        # 3. Find the correct key
        key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
        if not key:
            raise Exception("Public key not found")

        # 4. Verify and decode
        payload = jwt.decode(token, key, algorithms=['RS256'])

        user_id = payload.get("sub")
        if not user_id:
            raise Exception("No user_id in token")

        return str(user_id)

    except Exception as e:
        logger.error(f"Auth failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")