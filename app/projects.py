from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends

from app.db import get_async_session
from app.models import Project, User
from app.schemas import ProjectCreate, ProjectUpdate
from app.auth import current_active_user 

class ProjectManager:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session
        
    async def get_project(self, project_id: int):
        result = await self.session.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = result.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found."
            )
        return project
    
    async def create_project(self, project_data: ProjectCreate, user: User = Depends(current_active_user)):
        new_project = Project(
            **project_data.model_dump(),
            owner_id=user.id
        )
        self.session.add(new_project)
        await self.session.commit()
        await self.session.refresh(new_project)
        return new_project
    
    async def update_project(self, project_id: int, project_update: ProjectUpdate):
        project = await self.get_project(project_id)
        for key, value in project_update.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project      
    
    async def delete_project(self, project_id: int):
        project = await self.get_project(project_id)
        await self.session.delete(project)
        await self.session.commit()
        
async def get_project_manager(session: AsyncSession = Depends(get_async_session)):
    return ProjectManager(session)

async def current_active_project(
    project_id: int,
    project_manager: ProjectManager = Depends(get_project_manager),
):
    return await project_manager.get_project(project_id)
