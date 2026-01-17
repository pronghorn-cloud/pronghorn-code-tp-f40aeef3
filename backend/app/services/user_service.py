"""User Service

Business logic for user management.
"""

from typing import Optional, Tuple, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import pyotp
import secrets

from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            provider_id=data.provider_id,
            status=UserStatus.ACTIVE,
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        provider_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[User], int]:
        """List users with filtering and pagination."""
        query = select(User)
        count_query = select(func.count(User.id))
        
        # Apply filters
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        
        if status:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)
        
        if provider_id:
            query = query.where(User.provider_id == provider_id)
            count_query = count_query.where(User.provider_id == provider_id)
        
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    async def update(self, user_id: UUID, data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = await self.get_by_id(user_id)
        
        if not user:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Soft delete user (set status to inactive)."""
        user = await self.get_by_id(user_id)
        
        if not user:
            return False
        
        user.status = UserStatus.INACTIVE
        await self.db.flush()
        
        return True
    
    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp."""
        user = await self.get_by_id(user_id)
        
        if user:
            user.last_login = datetime.utcnow()
            await self.db.flush()
    
    async def change_password(self, user_id: UUID, new_password: str) -> None:
        """Change user password."""
        user = await self.get_by_id(user_id)
        
        if user:
            user.password_hash = get_password_hash(new_password)
            user.password_changed_at = datetime.utcnow()
            user.must_change_password = False
            await self.db.flush()
    
    async def setup_mfa(self, user_id: UUID) -> dict:
        """Setup MFA for user."""
        user = await self.get_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Generate secret
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        
        # Generate provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Claims Processing Platform"
        )
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        await self.db.flush()
        
        return {
            "secret": secret,
            "qr_code_url": provisioning_uri,
            "backup_codes": backup_codes
        }
    
    async def verify_mfa_code(self, user_id: UUID, code: str) -> bool:
        """Verify MFA code."""
        user = await self.get_by_id(user_id)
        
        if not user or not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(code)
    
    async def enable_mfa(self, user_id: UUID) -> None:
        """Enable MFA for user."""
        user = await self.get_by_id(user_id)
        
        if user:
            user.mfa_enabled = True
            await self.db.flush()
