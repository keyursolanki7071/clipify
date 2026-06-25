import os
import glob
import webvtt
import asyncio
from openai import AsyncOpenAI
import uuid
from app.core.config import settings

class TranscriberService:
    @staticmethod
    def _parse_time_to_seconds(time_str: str) -> float:
        # webvtt time format: HH:MM:SS.mmm
        h, m, s = time_str.split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)

    @staticmethod
    def _get_vtt_file(job_id: uuid.UUID) -> str | None:
        """Finds the downloaded VTT file for the given job_id."""
        pattern = f"tmp/{job_id}/*.vtt"
        files = glob.glob(pattern)
        if files:
            return files[0]
        return None

    @staticmethod
    async def run(video_path: str, job_id: uuid.UUID) -> list[dict]:
        """
        Attempts to read native YouTube VTT captions.
        Falls back to OpenAI Whisper API if missing.
        """
        # 1. Check for native VTT file
        vtt_file = TranscriberService._get_vtt_file(job_id)
        
        if vtt_file and os.path.exists(vtt_file):
            print("Found native YouTube captions, parsing...")
            transcript = []
            for caption in webvtt.read(vtt_file):
                # Clean up webvtt specific tags like <c> etc if they exist
                text = caption.text.strip().replace('<c>', '').replace('</c>', '')
                transcript.append({
                    "start": TranscriberService._parse_time_to_seconds(caption.start),
                    "end": TranscriberService._parse_time_to_seconds(caption.end),
                    "text": text
                })
            return transcript

        print("No native captions found. Falling back to OpenAI Whisper...")
        # 2. Fallback to OpenAI Whisper
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env. Cannot fallback to Whisper.")
        
        # Extract audio using ffmpeg to ensure we are uploading just audio and staying under limits
        audio_path = f"tmp/{job_id}/audio.mp3"
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        ffmpeg_path = os.path.join(local_app_data, 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe', 'ffmpeg-8.1.1-full_build', 'bin', 'ffmpeg.exe')
        
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = "ffmpeg" # fallback to system path
            
        cmd = [ffmpeg_path, "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]
        def run_ffmpeg():
            import subprocess
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
        await asyncio.to_thread(run_ffmpeg)
        
        # Upload to OpenAI
        print("Uploading audio to OpenAI Whisper API...")
        with open(audio_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            
        # Parse OpenAI response
        transcript = []
        if hasattr(response, 'segments') and response.segments:
            for segment in response.segments:
                transcript.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
                
        return transcript
