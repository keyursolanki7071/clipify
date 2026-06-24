import os
import uuid
import asyncio

class ClipperService:
    @staticmethod
    async def run(video_path: str, viral_clips: dict, job_id: uuid.UUID) -> dict:
        """
        Slices and crops the video into exactly 9:16 vertical segments based on viral clips.
        Returns a dictionary containing the output paths.
        """
        if not viral_clips or 'clips' not in viral_clips:
            raise ValueError("No clips to process.")
            
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        ffmpeg_path = os.path.join(local_app_data, 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe', 'ffmpeg-8.1.1-full_build', 'bin', 'ffmpeg.exe')
        
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = "ffmpeg" # fallback
            
        output_paths = []
        
        for index, clip in enumerate(viral_clips['clips']):
            start_time = clip['start_time']
            end_time = clip['end_time']
            
            output_path = f"tmp/{job_id}/clip_{index}.mp4"
            
            # Use -ss before -i for fast seeking, and crop=ih*9/16:ih for perfect center vertical crop
            cmd = (
                f'"{ffmpeg_path}" -ss {start_time} -to {end_time} -i "{video_path}" '
                f'-vf "crop=ih*9/16:ih" -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k '
                f'-y "{output_path}"'
            )
            
            print(f"Clipping segment {index} ({start_time} to {end_time}) with 9:16 crop...")
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"FFMPEG Error on clip {index}: {stderr.decode()}")
                raise RuntimeError(f"FFMPEG failed to crop clip {index}")
                
            output_paths.append({
                "url": f"http://localhost:8000/media/{job_id}/clip_{index}.mp4",
                "title": clip.get('hook', 'Untitled Clip'),
                "explanation": clip.get('why_viral', ''),
                "clip_type": clip.get('clip_type', 'story'),
                "target_platform": clip.get('target_platform', 'All'),
                "confidence": clip.get('confidence', 'medium'),
                "rank": clip.get('rank', index + 1)
            })
            
        return {
            "source_video": video_path,
            "clips": output_paths
        }
