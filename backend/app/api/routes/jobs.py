import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db_session
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.services.worker import process_video_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/", response_model=list[JobResponse])
async def list_jobs(db: AsyncSession = Depends(get_db_session)):
    """
    Get a list of all jobs, sorted by most recent first.
    """
    from sqlalchemy import select
    result = await db.execute(select(Job).order_by(Job.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=JobResponse, status_code=202)
async def create_job(
    job_in: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new video processing job.
    """
    # 1. Create job in DB
    new_job = Job(youtube_url=job_in.youtube_url, status="pending")
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # 2. Add background task
    background_tasks.add_task(process_video_job, new_job.id)
    
    # 3. Return accepted status and job ID
    return new_job

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)):
    """
    Get the status of a job.
    """
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
