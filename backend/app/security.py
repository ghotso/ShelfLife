"""
Security utilities for encryption and password hashing
"""
import bcrypt
from cryptography.fernet import Fernet
import os
import base64


def get_encryption_key():
    """Get or create encryption key for credentials"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    key_file = os.path.join(data_dir, ".encryption_key")
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key


def encrypt_token(token: str) -> str:
    """Encrypt a token/API key"""
    if not token:
        return ""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(token.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token/API key"""
    if not encrypted_token:
        return ""
    key = get_encryption_key()
    fernet = Fernet(key)
    try:
        decoded = base64.b64decode(encrypted_token.encode())
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode()
    except Exception:
        return ""


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

