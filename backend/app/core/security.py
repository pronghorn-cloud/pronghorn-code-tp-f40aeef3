"""Security Utilities

JWT token handling, password hashing, and encryption utilities.
HIPAA-compliant security implementations.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import hashlib

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """Create JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional JWT claims
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token.
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


class PHIEncryption:
    """HIPAA-compliant PHI encryption utilities.
    
    Uses Fernet (AES-128) encryption for PHI data at rest.
    """
    
    def __init__(self, key: Optional[str] = None):
        """Initialize encryption with key."""
        if key:
            # Derive a valid Fernet key from the provided key
            derived_key = base64.urlsafe_b64encode(
                hashlib.sha256(key.encode()).digest()
            )
            self.cipher = Fernet(derived_key)
        elif settings.PHI_ENCRYPTION_KEY:
            derived_key = base64.urlsafe_b64encode(
                hashlib.sha256(settings.PHI_ENCRYPTION_KEY.encode()).digest()
            )
            self.cipher = Fernet(derived_key)
        else:
            # Generate a key for development (NOT for production)
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive PHI data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt PHI data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


def hash_patient_id(patient_id: str) -> str:
    """Create a one-way hash of patient ID for pseudonymization."""
    return hashlib.sha256(f"{patient_id}{settings.SECRET_KEY}".encode()).hexdigest()


# Global PHI encryption instance
phi_encryption = PHIEncryption()
