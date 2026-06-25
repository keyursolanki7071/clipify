def get_classification_prompt(video_duration: int | None, video_topic: str, sample: str) -> str:
    return f"""
You are an expert video content strategist. Classify this video and define the optimal clipping strategy.
Duration: {video_duration or 'unknown'}s
Topic: {video_topic}

Transcript Sample:
{sample}
"""

def get_candidate_generation_prompt(category: str, prefer_long_context: bool, minimum_hook_score: int, formatted_chunk: str) -> str:
    return f"""
Analyze this transcript chunk to find candidate viral clips.
Strategy Category: {category}
Prefer long context: {prefer_long_context}
Minimum hook score required: {minimum_hook_score}

Find 3-5 candidate clips. Score each candidate meticulously on a scale of 1-10 for each metric.
Use the exact line IDs in the brackets.
A candidate clip should not be too short. Provide sufficient context.

Transcript:
{formatted_chunk}
"""

def get_review_prompt(category: str, full_context: str) -> str:
    return f"""
You are a Senior Editor. Review these candidate clips.
Strategy Category: {category}

For each candidate, you must:
1. Approve or Reject it. Reject if it starts mid-thought ("so...", "and..."), requires prior context, is boring, or ends abruptly without resolution.
2. Refine the start and end Line IDs to ensure perfect natural flow. You may expand or shrink the boundary using the provided context lines.
3. Ensure the start is strong and hooky. 
4. If approved, generate the hook_text, why_viral, clip_type, platform, confidence, and social_media_caption.
5. Rank the approved clips (1 is best).

CANDIDATES WITH CONTEXT (+/- 3 lines):
Lines marked with '-->' are the original proposed candidate. Unmarked lines are the surrounding context.
{full_context}
"""
