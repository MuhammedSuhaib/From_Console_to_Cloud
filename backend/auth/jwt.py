import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlmodel import Session
from database import get_session
import sqlalchemy
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user_id(
    creds = Depends(security), 
    db: Session = Depends(get_session)
) -> str:
    token = creds.credentials
    
    try:
        # We query the session table directly. Better Auth stores tokens as-is.
        # userId and expiresAt are standard Better Auth columns.
        query = sqlalchemy.text('SELECT "userId", "expiresAt" FROM "session" WHERE "token" = :t')
        result = db.execute(query, {"t": token}).fetchone()

        if not result:
            logger.warning(f"Invalid session token attempted: {token[:10]}")
            raise HTTPException(status_code=401, detail="Invalid session")

        user_id, expires_at = result
        
        # Check if the session has expired
        # Ensure timezone comparison is consistent
        if expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            logger.warning(f"Session expired for user: {user_id}")
            raise HTTPException(status_code=401, detail="Session expired")

        logger.info(f"User {user_id} authenticated successfully")
        return str(user_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth System Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Internal authentication failure")