from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.projects import ProjectManager, get_project_manager, current_active_project
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.auth import current_active_user
from typing import List

router = APIRouter()

@router.get("/projects", response_model=List[ProjectRead], tags=["projects"])
async def list_projects(
    session: AsyncSession = Depends(get_project_manager)
):
    result = await session.execute(select(Project))
    projects = result.scalars().all()
    if not projects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found.")
    return projects

@router.post("/projects", response_model=ProjectRead, tags=["projects"])
async def create_project(
    project_data: ProjectCreate,
    user=Depends(current_active_user),
    project_manager: ProjectManager = Depends(get_project_manager),
):
    return await project_manager.create_project(project_data, user)

@router.get("/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
async def get_project(
    project_id: int,
    project=Depends(current_active_project),
):
    return project

@router.put("/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    project_manager: ProjectManager = Depends(get_project_manager),
):
    return await project_manager.update_project(project_id, project_data)

@router.delete("/projects/{project_id}", tags=["projects"])
async def delete_project(
    project_id: int,
    project_manager: ProjectManager = Depends(get_project_manager),
):
    await project_manager.delete_project(project_id)
    return {"detail": "Project deleted successfully"}
