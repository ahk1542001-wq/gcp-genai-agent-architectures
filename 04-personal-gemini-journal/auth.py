"""
Authentication & Tenant Verification Layer for Personal Gemini Journal
Bakes in Principle of Least Privilege, cryptographic ID token validation,
and strict multi-tenant boundary checks.
"""

import os
import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import Header, HTTPException, status
import firebase_admin
from firebase_admin import auth as fb_auth

logger = logging.getLogger("auth")

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "intelligent-arc-488111-s0")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

_firebase_app = None


def get_firebase_app():
    """Initializes Firebase Admin SDK via Application Default Credentials and project ID."""
    global _firebase_app
    if _firebase_app is None:
        try:
            _firebase_app = firebase_admin.get_app()
        except ValueError:
            project_id = os.environ.get("GCP_PROJECT_ID", "intelligent-arc-488111-s0")
            _firebase_app = firebase_admin.initialize_app(options={"projectId": project_id})
    return _firebase_app


def test_auth_enabled() -> bool:
    """
    Checks if deterministic test authentication tokens are permitted.
    Only permitted when ENVIRONMENT is 'test' or 'development' AND ALLOW_TEST_AUTH is 'true'.
    Production MUST always fail closed and reject test tokens.
    """
    env = os.environ.get("ENVIRONMENT", "production").strip().lower()
    allow_test = os.environ.get("ALLOW_TEST_AUTH", "").strip().lower() == "true"
    return env in ("test", "development") and allow_test


class AuthenticatedUser(BaseModel):
    uid: str
    email: Optional[str] = None
    name: Optional[str] = "Reflective Traveler"
    auth_provider: str = "firebase"


def verify_firebase_id_token(token: str) -> AuthenticatedUser:
    """
    Cryptographically verifies a Firebase Authentication ID Token via Firebase Admin SDK.
    Validates signature, issuer, audience, and expiration.
    Deterministic test tokens are permitted ONLY when test_auth_enabled() is True.
    All failures fail closed with a stable public error message.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Deterministic Test Token Support (Hermetic Testing Only)
    is_test_token = token.startswith("test-token:") or token.startswith("mock-token:")
    is_demo_token = token == "demo-guest-token"

    if is_test_token or is_demo_token:
        if not test_auth_enabled():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if is_demo_token:
            return AuthenticatedUser(
                uid="demo_guest_user_123",
                email="demo.guest@cloudrun.local",
                name="Demo Explorer",
                auth_provider="demo_mode",
            )
        parts = token.split(":")
        uid = parts[1] if len(parts) > 1 else "test_user"
        email = parts[2] if len(parts) > 2 else f"{uid}@test.local"
        name = parts[3] if len(parts) > 3 else f"User {uid}"
        return AuthenticatedUser(uid=uid, email=email, name=name, auth_provider="test_harness")

    # 2. Production Verification via Firebase Admin SDK (ADC)
    try:
        get_firebase_app()
        decoded = fb_auth.verify_id_token(token)
        uid = decoded.get("uid") or decoded.get("sub")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return AuthenticatedUser(
            uid=uid,
            email=decoded.get("email"),
            name=decoded.get("name", "Journaler"),
            auth_provider=decoded.get("firebase", {}).get("sign_in_provider", "google.com"),
        )
    except HTTPException:
        raise
    except Exception as e:
        # Fail closed with stable public message; log only exception class
        logger.warning("Firebase token verification failed: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """
    FastAPI Dependency to inject verified AuthenticatedUser into route handlers.
    Requires Bearer token format: 'Authorization: Bearer <token>'
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization scheme. Format must be: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_firebase_id_token(token.strip())


def enforce_user_isolation(user: AuthenticatedUser, target_uid: str) -> None:
    """
    Security Gate: Enforces that the authenticated user strictly owns the
    target resource path (/users/{uid}/...).
    Rejects cross-tenant attempts with HTTP 403 Forbidden.
    """
    if user.uid != target_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Multi-tenant boundary violation. You do not own this journal path."
        )
