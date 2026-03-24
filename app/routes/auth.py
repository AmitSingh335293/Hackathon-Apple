"""
Auth Routes
Login, token refresh, and current-user endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List

from app.services.auth_service import AuthService
from app.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)
_auth_service = AuthService()


# ------------------------------------------------------------------ #
# Request / Response models                                           #
# ------------------------------------------------------------------ #

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    email: str
    full_name: str
    role: str
    permissions: List[str]

class UserProfile(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    permissions: List[str]


# ------------------------------------------------------------------ #
# Dependency — extract & verify Bearer token                          #
# ------------------------------------------------------------------ #

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """FastAPI dependency — returns the authenticated user payload or raises 401."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = _auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency — requires admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


# ------------------------------------------------------------------ #
# Endpoints                                                           #
# ------------------------------------------------------------------ #

@router.post("/login", response_model=LoginResponse, summary="Login with username & password")
async def login(request: LoginRequest):
    """
    Authenticate a user and return a Bearer token.
    The token encodes username, role, and table permissions.
    """
    user = _auth_service.authenticate(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    token = _auth_service.create_token(user)
    logger.info("Token issued", username=user["username"])
    return LoginResponse(
        access_token=token,
        username=user["username"],
        email=user.get("email", ""),
        full_name=user.get("full_name", user["username"]),
        role=user.get("role", "user"),
        permissions=user.get("permissions", []),
    )


@router.get("/me", response_model=UserProfile, summary="Get current user profile")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return UserProfile(
        username=current_user["sub"],
        email=current_user.get("email", ""),
        full_name=current_user.get("full_name", current_user["sub"]),
        role=current_user.get("role", "user"),
        permissions=current_user.get("permissions", []),
    )


@router.get("/users", summary="List all users (admin only)")
async def list_users(admin: dict = Depends(get_admin_user)):
    """Return all users — admin only."""
    return _auth_service.get_all_users()

