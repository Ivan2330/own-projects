import uuid
from datetime import datetime
from pydantic import BaseModel
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    full_name: str | None = None
    user_status: str

    class Config:
        orm_mode = True

class UserCreate(schemas.BaseUserCreate):
    full_name: str | None = None
    user_status: str

    class Config:
        orm_mode = True

class UserUpdate(schemas.BaseUserUpdate):
    full_name: str | None = None
    user_status: str

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    project_name: str
    project_status: str
    project_priority: str

    class Config:
        orm_mode = True
    
class ProjectCreate(ProjectBase):
    owner_id: uuid.UUID

class ProjectRead(ProjectBase):
    project_id: int
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProjectUpdate(BaseModel):
    project_name: str | None = None
    project_status: str | None = None
    project_priority: str | None = None
    owner_id: uuid.UUID | None = None

    class Config:
        orm_mode = True
        
class TaskBase(BaseModel):
    task_name: str
    project_id: int
    assignee_id: uuid.UUID

    class Config:
        orm_mode = True

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    task_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TaskUpdate(BaseModel):
    task_name: str | None = None
    project_id: int | None = None
    assignee_id: uuid.UUID | None = None

    class Config:
        orm_mode = True