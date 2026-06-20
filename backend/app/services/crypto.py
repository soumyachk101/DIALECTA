"""Fernet-based encryption for OAuth tokens (BACKEND_SCHEMA.md §4)."""
from cryptography.fernet import Fernet

from app.config import get_settings


def _fernet() -> Fernet:
    key = get_settings().token_encryption_key
    # Allow passing a 32-byte raw key (base64-url) or a Fernet key directly.
    try:
        return Fernet(key.encode())
    except Exception:
        # Derive a Fernet key from raw bytes via SHA256
        import base64
        import hashlib
        digest = hashlib.sha256(key.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_token(plaintext: str) -> bytes:
    return _fernet().encrypt(plaintext.encode())


def decrypt_token(ciphertext: bytes) -> str:
    return _fernet().decrypt(ciphertext).decode()
