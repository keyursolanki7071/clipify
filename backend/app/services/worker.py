import asyncio
import uuid
from app.db.engine import async_session_maker
from app.models.job import Job
from app.services.pipeline.downloader import DownloaderService
from app.services.pipeline.transcriber import TranscriberService
from app.services.pipeline.analyzer import AnalyzerService
import os

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
            video_path = f"tmp/{job_id}.mp4"
            
            # 0. Extract Metadata
            if not job.video_title:
                metadata = await asyncio.to_thread(DownloaderService.extract_metadata, job.youtube_url)
                job.video_title = metadata.get('title')
                job.video_thumbnail = metadata.get('thumbnail')
                job.video_duration = metadata.get('duration')
                await session.commit()
            
            # 1. Download Video
            if not os.path.exists(video_path):
                job.status = "downloading"
                job.progress = 0.0
                await session.commit()
                
                async def on_progress(percentage: float):
                    await update_job_progress(job_id, percentage)
                
                await DownloaderService.run(job.youtube_url, job.id, on_progress)
                job = await session.get(Job, job_id)
            
            # 2. Transcription
            if not job.transcript:
                job.status = "transcribing"
                job.progress = 0.0
                await session.commit()
                
                transcript = await TranscriberService.run(video_path, job_id)
                
                job = await session.get(Job, job_id)
                job.transcript = transcript
                await session.commit()
            
            # 3. Analyze
            if not job.viral_clips:
                job.status = "analyzing"
                await session.commit()
                
                viral_clips = await AnalyzerService.run(job.transcript, job.video_duration, job_id)
                
                job = await session.get(Job, job_id)
                job.viral_clips = viral_clips
                await session.commit()
            
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
