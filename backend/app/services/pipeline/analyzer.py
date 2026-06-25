import os
import uuid
import asyncio
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.core.config import settings
from typing import Literal
from app.services.pipeline.prompts import get_classification_prompt, get_candidate_generation_prompt, get_review_prompt

# --- STAGE 1: Classification & Strategy ---
class ClipStrategy(BaseModel):
    category: Literal["Podcast", "Interview", "Educational", "Stand-up Comedy", "Storytelling", "Motivational Speech", "News", "Vlog", "Gaming", "Other"] = Field(description="The primary category of the video")
    prefer_long_context: bool = Field(description="True if context buildup is important (e.g. stories/comedy)")
    prefer_complete_arguments: bool = Field(description="True if clips need full explanations (e.g. educational)")
    allow_storytelling: bool = Field(description="True if stories are acceptable clips")
    minimum_hook_score: int = Field(description="Minimum hook strength score (1-10) required for this category")

# --- STAGE 3: Candidate Generation ---
class CandidateMetrics(BaseModel):
    hook: int = Field(description="Score (1-10) for hook strength")
    emotion: int = Field(description="Score (1-10) for emotional impact")
    story: int = Field(description="Score (1-10) for storytelling/narrative arc")
    humor: int = Field(description="Score (1-10) for comedic value")
    novelty: int = Field(description="Score (1-10) for unexpectedness or novelty")
    retention: int = Field(description="Score (1-10) for potential viewer retention")
    shareability: int = Field(description="Score (1-10) for likelihood of sharing")

class RawCandidate(BaseModel):
    start_line_id: int = Field(description="Exact Line ID where the premise/setup of the clip begins")
    end_line_id: int = Field(description="Exact Line ID where the punchline/resolution of the clip ends")
    metrics: CandidateMetrics = Field(description="Engagement metrics for this candidate")

class Stage3Response(BaseModel):
    candidates: list[RawCandidate] = Field(description="List of raw candidate clips found in this chunk")

# --- STAGE 4: Reviewer & Refinement ---
class RefinedCandidate(BaseModel):
    approved: bool = Field(description="True if this candidate passes the strict review")
    start_line_id: int = Field(description="Refined exact Line ID to start the clip naturally")
    end_line_id: int = Field(description="Refined exact Line ID to end the clip with resolution")
    hook_text: str = Field(description="The exact first sentence of this clip that acts as the hook")
    why_viral: str = Field(description="1-2 sentences on exactly why this will perform")
    clip_type: Literal["story", "hot_take", "value_bomb", "relatable_moment", "shocking_stat"] = Field(description="Primary format")
    target_platform: Literal["TikTok", "Reels", "Shorts", "All"] = Field(description="Best suited platform")
    confidence: Literal["high", "medium", "low"] = Field(description="Confidence that this clip will perform well")
    social_media_caption: str = Field(description="A highly engaging caption for this clip including 3-5 viral hashtags")
    rank: int | None = Field(description="Final ranking of this clip among approved clips (1 is best)", default=None)
    rejection_reason: str | None = Field(description="If rejected, briefly explain why", default=None)

class Stage4Response(BaseModel):
    final_clips: list[RefinedCandidate] = Field(description="The reviewed, ranked, and refined final clips")


class AnalyzerService:
    @staticmethod
    def _log_llm_response(job_id: uuid.UUID, stage: str, response: BaseModel):
        """Helper to log LLM parsed responses to a file for debugging."""
        os.makedirs(f"tmp/{job_id}", exist_ok=True)
        log_path = f"tmp/{job_id}/llm_logs.txt"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"STAGE: {stage}\n")
            f.write(f"{'='*50}\n")
            f.write(response.model_dump_json(indent=2))
            f.write("\n")

    @staticmethod
    def _format_transcript(transcript: list[dict], offset: int = 0) -> str:
        """Compresses transcript into a token-efficient string with Line IDs."""
        lines = []
        for i, segment in enumerate(transcript):
            text = segment['text']
            lines.append(f"[{i + offset}]: {text}")
        return "\n".join(lines)

    @staticmethod
    async def _classify_and_strategize(client: AsyncOpenAI, transcript: list[dict], video_duration: int | None, video_topic: str, job_id: uuid.UUID) -> ClipStrategy:
        sample = AnalyzerService._format_transcript(transcript[:150])
        prompt = get_classification_prompt(video_duration, video_topic, sample)
        print("Stage 1: Classifying video and generating strategy...")
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a content strategist."},
                {"role": "user", "content": prompt}
            ],
            response_format=ClipStrategy,
        )
        parsed_response = completion.choices[0].message.parsed
        AnalyzerService._log_llm_response(job_id, "Stage 1: Classification & Strategy", parsed_response)
        return parsed_response

    @staticmethod
    def _chunk_transcript(transcript: list[dict], chunk_size=200, overlap=50) -> list[tuple[int, list[dict]]]:
        chunks = []
        start = 0
        while start < len(transcript):
            end = start + chunk_size
            chunk = transcript[start:end]
            chunks.append((start, chunk))
            if end >= len(transcript):
                break
            start += (chunk_size - overlap)
        return chunks

    @staticmethod
    async def _generate_and_score_candidates(client: AsyncOpenAI, chunks: list[tuple[int, list[dict]]], strategy: ClipStrategy, job_id: uuid.UUID) -> list[RawCandidate]:
        all_candidates = []
        for idx, (offset, chunk) in enumerate(chunks):
            formatted = AnalyzerService._format_transcript(chunk, offset=offset)
            prompt = get_candidate_generation_prompt(
                strategy.category, 
                strategy.prefer_long_context, 
                strategy.minimum_hook_score, 
                formatted
            )
            print(f"Stage 3: Generating candidates for chunk {idx+1}/{len(chunks)}...")
            try:
                completion = await client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a viral clip scouter."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=Stage3Response,
                )
                parsed = completion.choices[0].message.parsed
                if parsed:
                    AnalyzerService._log_llm_response(job_id, f"Stage 3: Candidate Generation (Chunk {idx+1})", parsed)
                    if parsed.candidates:
                        all_candidates.extend(parsed.candidates)
            except Exception as e:
                print(f"Error analyzing chunk {idx+1}: {e}")
                
            # Rate limit backoff for chunks
            if idx < len(chunks) - 1:
                await asyncio.sleep(5)
                
        return all_candidates

    @staticmethod
    def _filter_and_deduplicate(candidates: list[RawCandidate], transcript: list[dict]) -> list[dict]:
        processed = []
        for c in candidates:
            # Validate indices
            if c.start_line_id < 0 or c.end_line_id >= len(transcript) or c.start_line_id >= c.end_line_id:
                continue
            
            # Hard Filters (Duration)
            start_time = transcript[c.start_line_id]['start']
            end_time = transcript[c.end_line_id]['end']
            duration = end_time - start_time
            if duration < 12 or duration > 90:
                continue
                
            # Hard Filters (Hook)
            if c.metrics.hook < 5:
                continue
                
            # Hard filter: Text starts with "so" or ends with "anyway"
            start_text = transcript[c.start_line_id]['text'].strip().lower()
            end_text = transcript[c.end_line_id]['text'].strip().lower()
            if start_text.startswith("so ") or end_text.endswith(" anyway.") or end_text.endswith(" anyway"):
                continue

            # Calculate weighted viral score
            m = c.metrics
            score = (m.hook * 0.25) + (m.emotion * 0.20) + (m.retention * 0.20) + (m.novelty * 0.15) + (m.shareability * 0.10) + (m.story * 0.10)
            
            processed.append({
                "candidate": c,
                "score": score,
                "duration": duration
            })
            
        # Deduplication: sort by score descending, remove overlaps
        processed.sort(key=lambda x: x["score"], reverse=True)
        final_candidates = []
        
        def is_overlap(c1, c2):
            overlap_start = max(c1.start_line_id, c2.start_line_id)
            overlap_end = min(c1.end_line_id, c2.end_line_id)
            if overlap_start <= overlap_end:
                overlap_len = overlap_end - overlap_start
                len1 = c1.end_line_id - c1.start_line_id
                if overlap_len / max(1, len1) > 0.5: # 50% overlap means they are effectively the same clip idea
                    return True
            return False

        for p in processed:
            overlap = False
            for f in final_candidates:
                if is_overlap(p["candidate"], f["candidate"]):
                    overlap = True
                    break
            if not overlap:
                final_candidates.append(p)
                
        # Take top 15 candidates max to pass to reviewer
        print(f"Stage 3.5: Filtered down to {len(final_candidates[:15])} high-quality unique candidates.")
        return final_candidates[:15]

    @staticmethod
    async def _review_and_refine(client: AsyncOpenAI, candidates: list[dict], transcript: list[dict], strategy: ClipStrategy, job_id: uuid.UUID) -> list[RefinedCandidate]:
        if not candidates:
            return []
            
        context_blocks = []
        for idx, p in enumerate(candidates):
            c = p["candidate"]
            # get +/- 3 lines of context
            start_idx = max(0, c.start_line_id - 3)
            end_idx = min(len(transcript) - 1, c.end_line_id + 3)
            
            context_lines = []
            for i in range(start_idx, end_idx + 1):
                text = transcript[i]['text']
                marker = "-->" if c.start_line_id <= i <= c.end_line_id else "   "
                context_lines.append(f"{marker} [{i}]: {text}")
                
            block = f"CANDIDATE {idx+1} (Viral Score: {p['score']:.2f}/10):\n" + "\n".join(context_lines)
            context_blocks.append(block)
            
        full_context = "\n\n".join(context_blocks)
        
        prompt = get_review_prompt(strategy.category, full_context)
        print("Stage 4: Reviewing and refining candidates...")
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a ruthless Senior Video Editor. Optimize for engagement, not quantity."},
                {"role": "user", "content": prompt}
            ],
            response_format=Stage4Response,
        )
        parsed_response = completion.choices[0].message.parsed
        AnalyzerService._log_llm_response(job_id, "Stage 4: Review & Refine", parsed_response)
        return parsed_response.final_clips

    @staticmethod
    async def run(transcript: list[dict], video_duration: int | None, video_topic: str, job_id: uuid.UUID) -> dict:
        """
        Multi-stage pipeline: Classify -> Chunk -> Score & Generate -> Filter -> Review & Refine
        """
        if not transcript:
            raise ValueError("Transcript is empty. Cannot run AnalyzerService.")
            
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env. Cannot run AnalyzerService.")
            
        # Stage 1
        strategy = await AnalyzerService._classify_and_strategize(client, transcript, video_duration, video_topic, job_id)
        
        # Stage 2
        chunks = AnalyzerService._chunk_transcript(transcript)
        
        # Stage 3
        raw_candidates = await AnalyzerService._generate_and_score_candidates(client, chunks, strategy, job_id)
        
        # Stage 3.5
        filtered_candidates = AnalyzerService._filter_and_deduplicate(raw_candidates, transcript)
        
        # Stage 4
        final_refined = await AnalyzerService._review_and_refine(client, filtered_candidates, transcript, strategy, job_id)
        
        # Format final output
        final_clips = []
        approved_clips = [c for c in final_refined if c.approved]
        approved_clips.sort(key=lambda x: x.rank or 999)
        
        for idx, c in enumerate(approved_clips[:7]): # Top 7 max
            try:
                start_time = transcript[c.start_line_id]['start']
                end_time = transcript[c.end_line_id]['end']
                duration = end_time - start_time
                
                final_clips.append({
                    "rank": idx + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "hook": c.hook_text,
                    "why_viral": c.why_viral,
                    "clip_type": c.clip_type,
                    "target_platform": c.target_platform,
                    "confidence": c.confidence,
                    "social_media_caption": c.social_media_caption
                })
            except IndexError:
                print(f"Reviewer hallucinated Line IDs: start={c.start_line_id}, end={c.end_line_id}")
                continue
            
        return {"clips": final_clips, "total_clips_found": len(final_clips), "note": f"Processed via multi-stage pipeline. Category: {strategy.category}"}
