import os
import uuid
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.core.config import settings
from typing import Literal

class ViralClip(BaseModel):
    rank: int = Field(description="Ranking of the clip from 1 (best) onwards")
    start_time: float = Field(description="Exact start timestamp of the clip in seconds")
    end_time: float = Field(description="Exact end timestamp of the clip in seconds")
    duration: float = Field(description="Total duration of the clip in seconds")
    hook: str = Field(description="The exact first sentence of this clip that acts as the hook")
    why_viral: str = Field(description="1-2 sentences on exactly why this will perform — what emotion or reaction it triggers")
    clip_type: Literal["story", "hot_take", "value_bomb", "relatable_moment", "shocking_stat"] = Field(description="The primary format/style of this clip")
    target_platform: Literal["TikTok", "Reels", "Shorts", "All"] = Field(description="The platform this clip is best suited for")
    confidence: Literal["high", "medium", "low"] = Field(description="Confidence that this clip will perform well")

class CurationResult(BaseModel):
    clips: list[ViralClip] = Field(description="List of viral clips found")
    total_clips_found: int = Field(description="Total number of clips identified")
    note: str | None = Field(description="Optional editor notes", default=None)

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
    async def run(transcript: list[dict], video_duration: int | None, video_topic: str, job_id: uuid.UUID) -> dict:
        """
        Analyzes the transcript and returns viral clips based on advanced viral frameworks.
        """
        if not transcript:
            raise ValueError("Transcript is empty. Cannot run AnalyzerService.")
            
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env. Cannot run AnalyzerService.")
            
        formatted_transcript = AnalyzerService._format_transcript(transcript)
        
        prompt = f"""
You are a viral short-form content strategist with deep expertise in TikTok, Instagram Reels, and YouTube Shorts. You have a track record of identifying moments that stop the scroll.

## VIDEO CONTEXT
- Duration: {video_duration or 'unknown'} seconds
- Topic/Niche: {video_topic or 'General'}

## YOUR TASK
Analyze the transcript below and extract the best segments for short-form clips. Only surface a segment if it genuinely earns its place — quality over quantity.

## WHAT MAKES A SEGMENT WORTH CLIPPING
A segment is worth clipping if it contains at least ONE of:
- **Pattern interrupt**: A surprising stat, counterintuitive claim, or unexpected opinion that makes someone stop scrolling
- **Story arc**: A mini narrative with tension and resolution that fits in under 60 seconds
- **Practical value**: A tip, hack, or insight someone can immediately use or share
- **Emotional pull**: Something funny, relatable, inspiring, or shocking
- **Controversy or strong opinion**: A take that will make people comment or share

A segment is NOT worth clipping if it:
- Starts mid-thought with no context
- Requires knowledge of earlier parts of the video to understand
- Is just filler, transitions, or setup without payoff
- Ends abruptly without resolution

## HOOK QUALITY CHECK
The first 3 seconds of every clip must be able to stand alone as a hook. 
Good hooks are one of:
- A bold claim: "Most people get this completely wrong..."
- A curiosity gap: "Here's what nobody tells you about..."
- A relatable struggle: "If you've ever felt like..."
- A surprising stat or fact
- A direct challenge: "You're probably doing X — stop."

If the segment doesn't open with a natural hook from the transcript, expand the start timestamp slightly to include one, or skip the segment entirely.

## TIMESTAMPS & DURATION STRICT RULES (CRITICAL)
1. Do NOT just extract a single sentence or a single transcript line! A single line is usually 1-5 seconds long.
2. You MUST combine multiple continuous, sequential transcript lines to form a complete, coherent segment.
3. The `start_time` must be the exact start timestamp of the first line (the hook).
4. The `end_time` must be the exact end timestamp of a MUCH LATER line so that the total `duration` (end_time - start_time) is strictly between 30 and 60 seconds.
5. Ensure the segment has a natural conclusion. Do not cut off mid-word.

## OUTPUT FORMAT
Return a JSON array conforming to the provided schema. Only include clips you'd rate confidence: high or medium. 
Duration MUST be between 30 and 60 seconds. Do not force clips if strong ones don't exist — return an empty array with a note explaining why.

## TRANSCRIPT
{formatted_transcript}
"""

        print("Analyzing transcript with OpenAI (gpt-4o-mini)...")
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a viral short-form content strategist."},
                {"role": "user", "content": prompt}
            ],
            response_format=CurationResult,
        )
        
        result = completion.choices[0].message.parsed
        return result.model_dump() if result else {"clips": [], "total_clips_found": 0, "note": ""}
