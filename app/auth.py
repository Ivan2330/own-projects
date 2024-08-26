import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, BackgroundTasks, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.db import User, get_user_db
from app.utils import send_email

SECRET = settings.secret_key
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(timezone.utc) + timedelta(minutes=settings.expire_token_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=settings.algorithm)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.user_db.get_by_email(email)

    async def authenticate(self, request: Optional[Request], form_data: OAuth2PasswordRequestForm) -> Optional[User]:
        user = await self.user_db.get_by_email(form_data.username)
        if user is None or not self.verify_password(form_data.password, user.hashed_password):
            return None
        return user

    async def on_after_register(self, user: User, request: Optional[Request] = None, background_tasks: BackgroundTasks = None):
        token = create_access_token(data={"sub": str(user.id)})
        confirm_url = f"{settings.frontend_url}/verify-email?token={token}"
        background_tasks.add_task(send_email, subject="Confirm Your Email", recipients=[user.email], body=f"Please click the following link to confirm your email: {confirm_url}")
        print(f"User {user.id} has registered. Confirmation email sent to {user.email}.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_user(self, user: User) -> None:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
