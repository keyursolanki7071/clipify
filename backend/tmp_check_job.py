import asyncio
import uuid
import shutil
import os
from app.db.engine import async_session_maker
from app.models.job import Job
from app.services.worker import process_video_job

async def main():
    job_id = uuid.UUID("7f39a416-17c4-41f3-94ec-6235dab350b4")
    
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job:
            job.viral_clips = None
            job.result_paths = None
            job.status = "transcribed"
            job.error_message = None
            await session.commit()
            print("Job state reset to 'transcribed'.")
        else:
            print("Job not found.")
            return
            
    # delete the old clips if any exist so they don't conflict
    job_dir = f"tmp/{job_id}"
    for file in os.listdir(job_dir):
        if file.startswith("clip_"):
            os.remove(os.path.join(job_dir, file))
            print(f"Deleted old clip: {file}")
            
    print(f"Resuming job {job_id}...")
    try:
        await process_video_job(job_id)
        print("Job re-run successfully.")
    except Exception as e:
        print(f"Caught exception: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(main())
