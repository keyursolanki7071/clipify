from typing import Any

class Aggregator:
    @staticmethod
    def _get_timeline_average(timeline: list[dict], start_time: float, end_time: float, value_key: str) -> float:
        """Helper to get the average value from a timeline within a time window."""
        relevant_points = [p[value_key] for p in timeline if start_time <= p["time"] <= end_time]
        if not relevant_points:
            return 0.0
        return sum(relevant_points) / len(relevant_points)

    @staticmethod
    def _find_spikes(timeline: list[dict], value_key: str, threshold: float) -> list[tuple[float, float]]:
        """Finds contiguous blocks where the value exceeds the threshold."""
        spikes = []
        in_spike = False
        start_time = 0.0
        
        for p in timeline:
            val = p[value_key]
            if val >= threshold and not in_spike:
                in_spike = True
                start_time = p["time"]
            elif val < threshold and in_spike:
                in_spike = False
                end_time = p["time"]
                if end_time - start_time >= 2.0: # spike must last at least 2 seconds
                    spikes.append((start_time, end_time))
                    
        if in_spike:
            spikes.append((start_time, timeline[-1]["time"]))
            
        return spikes

    @staticmethod
    def _map_to_transcript(start_time: float, end_time: float, transcript: list[dict], target_duration: int = 45) -> tuple[int, int]:
        """Maps a time window to transcript line IDs, expanding to target duration."""
        if not transcript:
            return 0, 0
            
        # Expand around the center of the spike
        center = (start_time + end_time) / 2
        new_start = max(0, center - (target_duration / 2))
        new_end = center + (target_duration / 2)
        
        start_line = 0
        end_line = len(transcript) - 1
        
        for i, t in enumerate(transcript):
            if t['start'] >= new_start:
                start_line = max(0, i - 1)
                break
                
        for i in range(start_line, len(transcript)):
            if transcript[i]['end'] >= new_end:
                end_line = i
                break
                
        return start_line, end_line

    @staticmethod
    def run(candidates: list[Any], transcript: list[dict], audio_timeline: list[dict], vision_timeline: list[dict]) -> list[dict]:
        """
        Aggregates Semantic, Audio, and Visual features.
        Generates new candidates from A/V spikes, merges with LLM candidates, and scores them all.
        """
        from app.services.pipeline.analyzer import RawCandidate, CandidateMetrics
        
        print("Aggregator: Scanning for Audio spikes...")
        audio_spikes = Aggregator._find_spikes(audio_timeline, "energy", 0.5)
        print("Aggregator: Scanning for Vision spikes...")
        vision_spikes = Aggregator._find_spikes(vision_timeline, "motion", 0.3)
        
        # Generate new candidates from spikes
        all_candidates = list(candidates) # start with LLM candidates
        
        for (st, et) in audio_spikes:
            sl, el = Aggregator._map_to_transcript(st, et, transcript)
            metrics = CandidateMetrics(hook=8, emotion=10, story=5, humor=5, novelty=5, retention=8, shareability=8)
            all_candidates.append(RawCandidate(start_line_id=sl, end_line_id=el, metrics=metrics))
            
        for (st, et) in vision_spikes:
            sl, el = Aggregator._map_to_transcript(st, et, transcript)
            metrics = CandidateMetrics(hook=8, emotion=8, story=5, humor=5, novelty=10, retention=8, shareability=8)
            all_candidates.append(RawCandidate(start_line_id=sl, end_line_id=el, metrics=metrics))
            
        print(f"Aggregator: Synthesized {len(all_candidates) - len(candidates)} new candidates purely from audio/video signals.")
        
        processed = []
        for c in all_candidates:
            if c.start_line_id < 0 or c.end_line_id >= len(transcript) or c.start_line_id >= c.end_line_id:
                continue
                
            start_time = transcript[c.start_line_id]['start']
            end_time = transcript[c.end_line_id]['end']
            duration = end_time - start_time
            
            # Hard Filters
            if duration < 10 or duration > 180:
                continue
            if c.metrics.hook < 4:
                continue
            start_text = transcript[c.start_line_id]['text'].strip().lower()
            end_text = transcript[c.end_line_id]['text'].strip().lower()
            if start_text.startswith("so ") or end_text.endswith(" anyway.") or end_text.endswith(" anyway"):
                continue

            # Semantic Score (Language AI)
            m = c.metrics
            semantic_score = (m.hook * 0.25) + (m.emotion * 0.20) + (m.retention * 0.20) + (m.novelty * 0.15) + (m.shareability * 0.10) + (m.story * 0.10)
            
            # Audio Analysis Score
            audio_score = Aggregator._get_timeline_average(audio_timeline, start_time, end_time, "energy") * 10
            
            # Vision Analysis Score
            vision_score = Aggregator._get_timeline_average(vision_timeline, start_time, end_time, "motion") * 10
            
            # Feature Aggregation (Combined Score)
            combined_score = (semantic_score * 0.4) + (audio_score * 0.3) + (vision_score * 0.3)
            
            processed.append({
                "candidate": c,
                "score": combined_score,
                "duration": duration,
                "semantic": semantic_score,
                "audio": audio_score,
                "vision": vision_score
            })
            
        # Deduplication
        processed.sort(key=lambda x: x["score"], reverse=True)
        final_candidates = []
        
        def is_overlap(c1, c2):
            overlap_start = max(c1.start_line_id, c2.start_line_id)
            overlap_end = min(c1.end_line_id, c2.end_line_id)
            if overlap_start <= overlap_end:
                overlap_len = overlap_end - overlap_start
                len1 = c1.end_line_id - c1.start_line_id
                if overlap_len / max(1, len1) > 0.5:
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
                
        print(f"Aggregator: Finalized {len(final_candidates[:30])} multimodal candidates.")
        return final_candidates[:30]
