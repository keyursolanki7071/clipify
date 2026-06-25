import cv2
import numpy as np
import asyncio
import subprocess

class VisionAnalyzer:
    @staticmethod
    def _extract_motion_sync(video_path: str, fps_sample: int = 1) -> list[dict]:
        """
        Extracts motion intensity from video frames using FFmpeg raw piping for maximum speed.
        Samples 'fps_sample' frames per second.
        Returns a list of dictionaries with 'time' and 'motion'.
        """
        try:
            print("VisionAnalyzer: Extracting motion data via FFmpeg raw pipe...")
            width, height = 160, 90
            frame_size = width * height
            
            cmd = [
                "ffmpeg", 
                "-i", video_path, 
                "-vf", f"fps={fps_sample},scale={width}:{height},format=gray", 
                "-f", "rawvideo", 
                "-pix_fmt", "gray", 
                "-"
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            timeline = []
            prev_frame = None
            time_sec = 0.0
            frame_count = 0
            
            while True:
                raw_bytes = process.stdout.read(frame_size)
                if not raw_bytes or len(raw_bytes) != frame_size:
                    break
                    
                frame = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((height, width))
                
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, frame)
                    motion_score = np.mean(diff)
                    timeline.append({
                        "time": float(time_sec),
                        "motion": float(motion_score)
                    })
                else:
                    timeline.append({
                        "time": float(time_sec),
                        "motion": 0.0
                    })
                    
                prev_frame = frame
                time_sec += (1.0 / fps_sample)
                frame_count += 1
                
                if frame_count % 500 == 0:
                    print(f"VisionAnalyzer: Processed {frame_count} scaled frames from FFmpeg pipe...")
                    
            process.stdout.close()
            process.wait()
            
            print(f"VisionAnalyzer: Finished. Total extracted frames: {frame_count}.")
            
            # Normalize motion scores to 0-1
            if timeline:
                max_motion = max(item["motion"] for item in timeline)
                if max_motion > 0:
                    for item in timeline:
                        item["motion"] = item["motion"] / max_motion
                        
            return timeline
            
        except Exception as e:
            print(f"VisionAnalyzer Error: {e}")
            return []

    @staticmethod
    async def run(video_path: str) -> list[dict]:
        return await asyncio.to_thread(VisionAnalyzer._extract_motion_sync, video_path)
