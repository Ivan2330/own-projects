from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from app.auth import auth_backend, fastapi_users, current_active_user, create_access_token
from app.schemas import UserRead, UserUpdate
from app.config import settings
from app.utils import send_email
from app.models import User
from app.auth import get_user_manager
from datetime import timedelta

router = APIRouter()

# Додавання стандартних роутів для аутентифікації
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
router.include_router(fastapi_users.get_register_router(UserRead, UserUpdate), prefix="/auth", tags=["auth"])
router.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
router.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])

# Додавання стандартних роутів для роботи з користувачами
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@router.post("/auth/jwt/login", tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    background_tasks: BackgroundTasks = None, 
    user_manager = Depends(get_user_manager)
):
    user = await user_manager.authenticate(request=None, form_data=form_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    token = create_access_token(data={"sub": str(user.id)})
    
    background_tasks.add_task(
        send_email,
        subject="Welcome!",
        recipients=[user.email],
        body=f"Welcome to our service, {user.full_name}!",
    )
    
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/request-reset-password", tags=["auth"])
async def request_reset_password(
    email: EmailStr, 
    background_tasks: BackgroundTasks, 
    user_manager = Depends(get_user_manager)
):
    user = await user_manager.get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=1))
    
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"
    background_tasks.add_task(
        send_email,
        subject="Reset Your Password",
        recipients=[user.email],
        body=f"Please click the following link to reset your password: {reset_url}",
    )
    
    return {"message": "Password reset email sent"}

@router.get("/users/me", response_model=UserRead, tags=["users"])
async def read_users_me(current_user: User = Depends(current_active_user)):
    return current_user

@router.get("/users/me/role", response_model=UserRead, tags=["users"])
async def check_user_role(current_user: User = Depends(current_active_user)):
    return {"user_status": current_user.user_status}
