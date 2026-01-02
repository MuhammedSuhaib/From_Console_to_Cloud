from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer
from sqlmodel import Session, select
from models import User
from schemas.task import UserResponse
from auth.jwt import create_access_token, get_current_user_id
from passlib.context import CryptContext
from database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

@router.post("/register")
def register_user(name: str = Form(...), email: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    """Register a new user."""

    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(password)

    # Create new user
    user = User(
        id=email,  # Using email as ID for simplicity
        email=email,
        name=name,
        hashed_password=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create JWT token
    access_token = create_access_token(data={"sub": user.id})

    return {"access_token": access_token, "user": user}

@router.post("/token")
def login_user(email: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    """Authenticate user and return access token."""

    # Find user by email
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": user.id})

    return {"access_token": access_token, "user": user}

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: str = Depends(get_current_user_id), session: Session = Depends(get_session)):
    """Get current user based on JWT token."""
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user