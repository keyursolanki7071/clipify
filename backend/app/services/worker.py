import asyncio
import uuid
from app.db.engine import async_session_maker
from app.models.job import Job

async def process_video_job(job_id: uuid.UUID):
    """
    Dummy background task that simulates the video processing pipeline.
    """
    async with async_session_maker() as session:
        # Simulate download
        await asyncio.sleep(3)
        job = await session.get(Job, job_id)
        if job:
            job.status = "downloading"
            await session.commit()
            
        # Simulate transcription
        await asyncio.sleep(3)
        job = await session.get(Job, job_id)
        if job:
            job.status = "transcribing"
            await session.commit()
            
        # Simulate analyzing
        await asyncio.sleep(3)
        job = await session.get(Job, job_id)
        if job:
            job.status = "analyzing"
            await session.commit()
            
        # Simulate clipping
        await asyncio.sleep(3)
        job = await session.get(Job, job_id)
        if job:
            job.status = "clipping"
            await session.commit()
            
        # Simulate completion
        await asyncio.sleep(3)
        job = await session.get(Job, job_id)
        if job:
            job.status = "completed"
            job.result_paths = {
                "clips": [
                    "/dummy/path/clip1.mp4",
                    "/dummy/path/clip2.mp4"
                ]
            }
            await session.commit()
