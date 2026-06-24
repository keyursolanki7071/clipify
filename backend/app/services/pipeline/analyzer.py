import os
import uuid
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.core.config import settings
from typing import Literal

class ViralClip(BaseModel):
    rank: int = Field(description="Ranking of the clip from 1 (best) onwards")
    start_line_id: int = Field(description="Exact Line ID where the premise/setup of the clip begins")
    end_line_id: int = Field(description="Exact Line ID where the punchline/resolution of the clip ends")
    duration: float = Field(description="Estimated duration of the clip in seconds")
    hook: str = Field(description="The exact first sentence of this clip that acts as the hook")
    why_viral: str = Field(description="1-2 sentences on exactly why this will perform — what emotion or reaction it triggers")
    clip_type: Literal["story", "hot_take", "value_bomb", "relatable_moment", "shocking_stat"] = Field(description="The primary format/style of this clip")
    target_platform: Literal["TikTok", "Reels", "Shorts", "All"] = Field(description="The platform this clip is best suited for")
    confidence: Literal["high", "medium", "low"] = Field(description="Confidence that this clip will perform well")
    social_media_caption: str = Field(description="A highly engaging caption for this clip including 3-5 viral hashtags, ready to copy-paste on TikTok/Reels/Shorts")

class CurationResult(BaseModel):
    clips: list[ViralClip] = Field(description="List of viral clips found")
    total_clips_found: int = Field(description="Total number of clips identified")
    note: str | None = Field(description="Optional editor notes", default=None)

class AnalyzerService:
    @staticmethod
    def _format_transcript(transcript: list[dict], offset: int = 0) -> str:
        """Compresses transcript into a token-efficient string with Line IDs."""
        lines = []
        for i, segment in enumerate(transcript):
            text = segment['text']
            lines.append(f"[Line {i + offset}]: {text}")
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
            
        # Chunking transcript to stay under 30,000 TPM limit
        chunks = []
        current_chunk = []
        current_length = 0
        for segment in transcript:
            text_len = len(segment['text'])
            if current_length + text_len > 60000: # ~15,000 tokens
                chunks.append(current_chunk)
                current_chunk = []
                current_length = 0
            current_chunk.append(segment)
            current_length += text_len
        if current_chunk:
            chunks.append(current_chunk)

        all_clips = []
        global_offset = 0
        
        import asyncio
        
        for idx, chunk in enumerate(chunks):
            formatted_transcript = AnalyzerService._format_transcript(chunk, offset=global_offset)
            
            prompt = f"""
You are a viral short-form content strategist with deep expertise in TikTok, Instagram Reels, and YouTube Shorts. You have a track record of identifying moments that stop the scroll.

## VIDEO CONTEXT
- Duration: {video_duration or 'unknown'} seconds
- Topic/Niche: {video_topic or 'General'}

## YOUR TASK
Analyze the transcript below and extract the best 3-7 short-form segments. The clips should be highly engaging, but do not be so strict that you reject good content. Focus on finding the funniest, most relatable, or most value-driven moments.

## THE ANATOMY OF A GOOD CLIP
A segment is worth clipping if it contains at least ONE of:
1. **The Hook**: A bold claim, a relatable statement, or an interesting question that stops the scroll.
2. **Tension & Payoff**: A story buildup followed by a funny punchline or interesting conclusion.
3. **No Dead Air**: The segment must be relatively dense with talking or action.
4. **Cultural Relevance**: Relatable everyday observations or opinions.
5. **Pattern interrupt**: A surprising stat, counterintuitive claim, or unexpected opinion that makes someone stop scrolling
6. **Emotional pull**: Something funny, relatable, inspiring, or shocking

A segment is NOT worth clipping if it:
- Starts mid-thought with no context
- Requires knowledge of earlier parts of the video to understand
- Is just filler, transitions, or setup without payoff
- Ends abruptly without resolution

## COMEDY & SETUP RULES (CRITICAL)
If the video is Stand-up Comedy or a story, you MUST start the clip at the BEGINNING of the premise/setup. 
DO NOT start the clip at the punchline. The audience needs the context to find it funny.

## TIMESTAMPS & LINE IDs (CRITICAL)
1. You MUST use the exact Line IDs provided in the transcript.
2. The `start_line_id` MUST be the Line ID of the very first sentence of the premise/hook.
3. The `end_line_id` MUST be the Line ID of the punchline or conclusion.
4. The estimated duration (difference in lines) should represent roughly 30 to 60 seconds of speaking (usually 10-30 lines depending on pace).
5. DO NOT just extract a single line.

## MULTI-LINGUAL CAPABILITIES (CRITICAL)
The transcript may be in Hindi, Hinglish, Spanish, or any other language. 
You are fluent in all languages and cultural slang. 
Analyze the humor, emotion, and context NATIVELY in the original language to find the absolute best viral hooks.
However, you MUST output your JSON metadata (`hook`, `why_viral`, `clip_type`, etc.) entirely in ENGLISH.

## OUTPUT FORMAT
Return a JSON array conforming to the provided schema. Only include clips you'd rate confidence: high or medium. 

## TRANSCRIPT CHUNK
{formatted_transcript}
"""
            print(f"Analyzing transcript chunk {idx + 1}/{len(chunks)} with OpenAI (gpt-4o)...")
            completion = await client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a viral short-form content strategist."},
                    {"role": "user", "content": prompt}
                ],
                response_format=CurationResult,
            )
            
            result = completion.choices[0].message.parsed
            if result and result.clips:
                all_clips.extend(result.clips)
                
            global_offset += len(chunk)
            
            # Rate limit backoff: if there are more chunks to process, wait 60s to reset TPM
            if idx < len(chunks) - 1:
                print("Waiting 60 seconds to respect OpenAI TPM rate limits before next chunk...")
                await asyncio.sleep(60)

        # Map Line IDs back to absolute timestamps for FFmpeg
        final_clips = []
        for c in all_clips:
            try:
                start_time = transcript[c.start_line_id]['start']
                end_time = transcript[c.end_line_id]['end']
                duration = end_time - start_time
                
                # Only keep clips > 15s to filter out hallucinations
                if duration >= 15:
                    final_clips.append({
                        "rank": c.rank,
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration": duration,
                        "hook": c.hook,
                        "why_viral": c.why_viral,
                        "clip_type": c.clip_type,
                        "target_platform": c.target_platform,
                        "confidence": c.confidence,
                        "social_media_caption": c.social_media_caption
                    })
            except IndexError:
                print(f"AI hallucinated Line IDs: start={c.start_line_id}, end={c.end_line_id}")
                continue

        # Sort by rank and re-assign
        final_clips.sort(key=lambda x: x["rank"])
        for i, c in enumerate(final_clips):
            c["rank"] = i + 1

        return {"clips": final_clips, "total_clips_found": len(final_clips), "note": "Processed in chunks"}
