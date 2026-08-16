"""Password hashing and opaque session helpers without storing raw credentials."""
import hashlib
import hmac
import secrets
from base64 import b64decode, b64encode
from datetime import datetime, timezone


PASSWORD_ALGORITHM = "scrypt"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
    )
    return "$".join((PASSWORD_ALGORITHM, b64encode(salt).decode(), b64encode(password_hash).decode()))


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, encoded_salt, encoded_hash = stored_hash.split("$", 2)
        if algorithm != PASSWORD_ALGORITHM:
            return False
        calculated_hash = hashlib.scrypt(
            password.encode("utf-8"), salt=b64decode(encoded_salt), n=2**14, r=8, p=1, dklen=32
        )
        return hmac.compare_digest(calculated_hash, b64decode(encoded_hash))
    except (ValueError, TypeError):
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    """Return an aware UTC timestamp for PostgreSQL-compatible comparisons."""
    return datetime.now(timezone.utc)


def session_has_expired(expires_at: datetime) -> bool:
    """Compare session timestamps safely across PostgreSQL and legacy SQLite."""
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= utc_now()
