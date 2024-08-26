from fastapi import APIRouter, Depends
from app.tasks import TaskManager, get_task_manager
from app.schemas import TaskCreate, TaskUpdate, TaskRead
from app.auth import current_active_user, User

router = APIRouter()

@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    user: User = Depends(current_active_user),
    task_manager: TaskManager = Depends(get_task_manager),
):
    return await task_manager.create_task(task_data, user)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    user: User = Depends(current_active_user),
    task_manager: TaskManager = Depends(get_task_manager),
):
    return await task_manager.get_task_for_user(task_id, user)

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user: User = Depends(current_active_user),
    task_manager: TaskManager = Depends(get_task_manager),
):
    return await task_manager.update_task(task_id, task_data, user)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user: User = Depends(current_active_user),
    task_manager: TaskManager = Depends(get_task_manager),
):
    await task_manager.delete_task(task_id, user)
    return {"detail": "Task deleted successfully"}
