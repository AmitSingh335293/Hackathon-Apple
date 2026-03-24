"""
Auth Service
Handles user authentication, JWT token creation/verification,
and user policy loading from data/users.json
"""

import json
import os
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.utils import get_logger

logger = get_logger(__name__)

SECRET_KEY = os.environ.get("AUTH_SECRET_KEY", "voicegenie-secret-key-change-in-production")
TOKEN_EXPIRE_HOURS = 8
USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "users.json")


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def _sign(header: str, body: str) -> str:
    """HMAC-SHA256 signature over header.body"""
    msg = f"{header}.{body}".encode()
    return _b64url_encode(hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).digest())


def _create_token(payload: dict) -> str:
    """Create a signed JWT-style token: header.payload.signature"""
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = _b64url_encode(json.dumps(payload).encode())
    signature = _sign(header, body)
    return f"{header}.{body}.{signature}"


def _verify_token(token: str) -> Optional[dict]:
    """Verify token signature and expiry. Returns payload dict or None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, body, signature = parts
        expected = _sign(header, body)
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(_b64url_decode(body))
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            return None
        return payload
    except Exception as e:
        logger.warning("Token verification failed", error=str(e))
        return None


class AuthService:
    """
    Manages user authentication and authorization.
    Users are defined in data/users.json.
    """

    def __init__(self):
        self._users: List[Dict[str, Any]] = []
        self._load_users()

    def _load_users(self):
        try:
            path = os.path.abspath(USERS_FILE)
            with open(path, "r") as f:
                self._users = json.load(f)
            logger.info("Users loaded", count=len(self._users))
        except FileNotFoundError:
            logger.error("users.json not found", path=USERS_FILE)
            self._users = []
        except Exception as e:
            logger.error("Failed to load users", error=str(e))
            self._users = []

    def _find_user(self, username: str) -> Optional[Dict[str, Any]]:
        for u in self._users:
            if u["username"].lower() == username.lower():
                return u
        return None

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify credentials. Returns user dict (without password) or None."""
        user = self._find_user(username)
        if not user:
            logger.warning("Login failed — unknown user", username=username)
            return None
        if password != user.get("password", ""):
            logger.warning("Login failed — wrong password", username=username)
            return None
        logger.info("Login successful", username=username, role=user.get("role"))
        return {k: v for k, v in user.items() if k != "password"}

    def create_token(self, user: Dict[str, Any]) -> str:
        """Create a signed bearer token for the authenticated user."""
        payload = {
            "sub": user["username"],
            "email": user.get("email", ""),
            "role": user.get("role", "user"),
            "permissions": user.get("permissions", []),
            "full_name": user.get("full_name", user["username"]),
            "exp": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)).timestamp(),
            "iat": datetime.utcnow().timestamp(),
        }
        return _create_token(payload)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token and return payload or None."""
        return _verify_token(token)

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        user = self._find_user(username)
        if not user:
            return None
        return {k: v for k, v in user.items() if k != "password"}

    def get_all_users(self) -> List[Dict[str, Any]]:
        return [{k: v for k, v in u.items() if k != "password"} for u in self._users]

