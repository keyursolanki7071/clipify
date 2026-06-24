import asyncio
import uuid
from app.db.engine import async_session_maker
from app.models.job import Job
from app.services.pipeline.downloader import DownloaderService

async def update_job_progress(job_id: uuid.UUID, progress: float):
    """Fire-and-forget helper to update progress without blocking."""
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job:
            job.progress = progress
            await session.commit()

async def process_video_job(job_id: uuid.UUID):
    """
    Background task that drives the video processing pipeline.
    """
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if not job:
            return
            
        try:
            # 0. Extract Metadata
            metadata = await asyncio.to_thread(DownloaderService.extract_metadata, job.youtube_url)
            job.video_title = metadata.get('title')
            job.video_thumbnail = metadata.get('thumbnail')
            job.video_duration = metadata.get('duration')
            
            # 1. Download Video
            job.status = "downloading"
            job.progress = 0.0
            await session.commit()
            
            async def on_progress(percentage: float):
                await update_job_progress(job_id, percentage)
            
            video_path = await DownloaderService.run(job.youtube_url, job.id, on_progress)
            
            # Refresh job from DB after long-running operation
            job = await session.get(Job, job_id)
            
            # 2. Simulate transcription
            job.status = "transcribing"
            job.progress = 0.0
            await session.commit()
            await asyncio.sleep(3)
            
            # 3. Simulate analyzing
            job.status = "analyzing"
            await session.commit()
            await asyncio.sleep(3)
            
            # 4. Simulate clipping
            job.status = "clipping"
            await session.commit()
            await asyncio.sleep(3)
            
            # 5. Simulate completion
            job.status = "completed"
            job.progress = 100.0
            job.result_paths = {
                "clips": [
                    "/dummy/path/clip1.mp4",
                    "/dummy/path/clip2.mp4"
                ],
                "source_video": video_path
            }
            await session.commit()
            
        except Exception as e:
            # Log failure and update DB
            print(f"Job failed: {e}")
            job = await session.get(Job, job_id) # Refresh instance
            job.status = "failed"
            job.error_message = str(e)
            await session.commit()
