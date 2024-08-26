from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends

from app.db import get_async_session
from app.models import Task, Project, User
from app.schemas import TaskCreate, TaskUpdate



class TaskManager:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_task(self, task_id: int) -> Task:
        result = await self.session.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalars().first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Task not found",
            )

        return task

    async def get_task_for_user(self, task_id: int, user: User) -> Task:
        task = await self.get_task(task_id)

        if task.assignee_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this task.",
            )

        return task

    async def create_task(self, task_data: TaskCreate, user: User) -> Task:
        project_result = await self.session.execute(select(Project).where(Project.project_id == task_data.project_id))
        project = project_result.scalars().first()

        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        new_task = Task(**task_data.model_dump(), assignee_id=user.id)
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)

        return new_task
    
    async def update_task(self, task_id: int, task_data: TaskUpdate, user: User) -> Task:
        task = await self.get_task_for_user(task_id, user)

        for key, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, task_id: int, user: User):
        task = await self.get_task_for_user(task_id, user)

        await self.session.delete(task)
        await self.session.commit()
        
async def get_task_manager(session: AsyncSession = Depends(get_async_session)):
    return TaskManager(session)
