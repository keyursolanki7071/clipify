import os
import uuid
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.core.config import settings

class ViralClip(BaseModel):
    title: str = Field(description="Catchy hook title for the clip")
    explanation: str = Field(description="Why this clip will go viral on TikTok/Shorts")
    start_time: float = Field(description="Exact start timestamp of the clip in seconds")
    end_time: float = Field(description="Exact end timestamp of the clip in seconds")

class CurationResult(BaseModel):
    clips: list[ViralClip] = Field(description="List of exactly 2 viral clips, each 30 to 60 seconds long")

class AnalyzerService:
    @staticmethod
    def _format_transcript(transcript: list[dict]) -> str:
        """Compresses transcript into a token-efficient string."""
        lines = []
        for segment in transcript:
            start = round(segment['start'], 2)
            end = round(segment['end'], 2)
            text = segment['text']
            lines.append(f"[{start} -> {end}]: {text}")
        return "\n".join(lines)

    @staticmethod
    async def run(transcript: list[dict], video_duration: int | None, job_id: uuid.UUID) -> dict:
        """
        Analyzes the transcript and returns exactly 2 viral clips.
        """
        if not transcript:
            raise ValueError("Transcript is empty. Cannot run AnalyzerService.")
            
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env. Cannot run AnalyzerService.")
            
        formatted_transcript = AnalyzerService._format_transcript(transcript)
        
        prompt = f"""
You are an expert social media content curator for TikTok, Instagram Reels, and YouTube Shorts.
I will provide you with a video transcript. The video is approximately {video_duration or 'unknown'} seconds long.

Your goal is to find exactly 2 highly engaging, viral segments from this video.
Each segment MUST be between 30 and 60 seconds long.
Each segment should have a clear hook, a main point, and a satisfying conclusion.

Return the EXACT start and end timestamps from the transcript that encompass each segment.

Transcript:
{formatted_transcript}
"""

        print("Analyzing transcript with OpenAI (gpt-4o-mini)...")
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert social media curator."},
                {"role": "user", "content": prompt}
            ],
            response_format=CurationResult,
        )
        
        result = completion.choices[0].message.parsed
        return result.model_dump() if result else {"clips": []}
