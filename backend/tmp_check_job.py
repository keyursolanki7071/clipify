import asyncio
import uuid
from app.db.engine import async_session_maker
from app.models.job import Job
from app.services.worker import process_video_job

async def main():
    job_id = uuid.UUID("7f39a416-17c4-41f3-94ec-6235dab350b4")
    
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        job.status = "downloading"
        job.error_message = None
        await session.commit()
        
    print(f"Resuming job {job_id}...")
    try:
        await process_video_job(job_id)
    except Exception as e:
        print(f"Caught exception: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(main())
