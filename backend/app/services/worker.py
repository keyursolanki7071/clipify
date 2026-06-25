import asyncio
import uuid
from app.db.engine import async_session_maker
from app.models.job import Job
from app.services.pipeline.downloader import DownloaderService
from app.services.pipeline.transcriber import TranscriberService
from app.services.pipeline.analyzer import AnalyzerService
from app.services.pipeline.clipper import ClipperService
import os
import traceback

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
            os.makedirs(f"tmp/{job_id}", exist_ok=True)
            video_path = f"tmp/{job_id}/source.mp4"
            
            # 0. Extract Metadata
            if not job.video_title:
                metadata = await asyncio.to_thread(DownloaderService.extract_metadata, job.youtube_url)
                title = metadata.get('title', 'Unknown Video')
                channel = metadata.get('channel', 'Unknown Channel')
                cats = metadata.get('categories', [])
                tags = metadata.get('tags', [])[:10]
                
                context_str = f"Title: {title} | Channel: {channel} | Categories: {', '.join(cats)} | Tags: {', '.join(tags)}"
                
                job.video_title = context_str
                job.video_thumbnail = metadata.get('thumbnail')
                job.video_duration = metadata.get('duration')
                await session.commit()
            
            job = await session.get(Job, job_id)
            if job.status == "cancelled": return

            # 1. Download Video
            if not os.path.exists(video_path):
                job.status = "downloading"
                job.progress = 0.0
                await session.commit()
                
                async def on_progress(percentage: float):
                    await update_job_progress(job_id, percentage)
                
                await DownloaderService.run(job.youtube_url, job.id, on_progress)
                job = await session.get(Job, job_id)
            
            if job.status == "cancelled": return

            # 2. Transcription
            if not job.transcript:
                job.status = "transcribing"
                job.progress = 0.0
                await session.commit()
                
                transcript = await TranscriberService.run(video_path, job_id)
                
                job = await session.get(Job, job_id)
                job.transcript = transcript
                await session.commit()
            
            job = await session.get(Job, job_id)
            if job.status == "cancelled": return

            # 3. Analyze
            if not job.viral_clips:
                job.status = "analyzing"
                await session.commit()
                
                viral_clips = await AnalyzerService.run(job.transcript, job.video_duration, job.video_title, job_id, video_path)
                
                job = await session.get(Job, job_id)
                job.viral_clips = viral_clips
                await session.commit()
            
            job = await session.get(Job, job_id)
            if job.status == "cancelled": return

            # 4. Clipping
            if not job.result_paths:
                job.status = "clipping"
                await session.commit()
                
                result_paths = await ClipperService.run(video_path, job.viral_clips, job_id)
                
                job = await session.get(Job, job_id)
                job.status = "completed"
                job.progress = 100.0
                job.result_paths = result_paths
                await session.commit()
            
        except asyncio.CancelledError:
            print(f"Job {job_id} cancelled by system.")
            job = await session.get(Job, job_id)
            if job.status != "cancelled":
                job.status = "failed"
                job.error_message = "Server restarted or job was cancelled."
            await session.commit()
            raise # Propagate cancellation
        except Exception as e:
            # Log failure and update DB
            error_details = traceback.format_exc()
            print(f"Job {job_id} failed: {e}\n{error_details}")
            job = await session.get(Job, job_id)
            job.status = "failed"
            job.error_message = str(e) or "Unknown error occurred (see logs)"
            await session.commit()
