import os
import time
import uuid
import asyncio
import yt_dlp
from typing import Callable, Awaitable

class DownloaderService:
    @staticmethod
    def extract_metadata(url: str) -> dict:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration')
            }

    @staticmethod
    def _download_sync(url: str, job_id: uuid.UUID, update_progress_cb: Callable[[float], Awaitable[None]], loop: asyncio.AbstractEventLoop) -> str:
        output_path = f"tmp/{job_id}.mp4"
        
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        ffmpeg_path = os.path.join(local_app_data, 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe', 'ffmpeg-8.1.1-full_build', 'bin')
        
        last_update_time = time.time()
        downloaded_files = set()
        current_file = None
        
        def progress_hook(d):
            nonlocal last_update_time, downloaded_files, current_file
            
            if d['status'] == 'finished':
                filename = d.get('filename')
                if filename:
                    downloaded_files.add(filename)
                    
            if d['status'] == 'downloading':
                filename = d.get('filename')
                if filename and filename != current_file:
                    current_file = filename

                current_time = time.time()
                if current_time - last_update_time > 1.0:
                    last_update_time = current_time
                    
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    
                    if total and total > 0:
                        file_progress = downloaded / total
                        
                        info = d.get('info_dict', {})
                        requested_downloads = info.get('requested_downloads')
                        total_files = len(requested_downloads) if requested_downloads else 1
                        
                        if total_files > 1:
                            num_completed = len(downloaded_files)
                            if num_completed == 0:
                                overall_progress = file_progress * 85
                            else:
                                overall_progress = 85 + (file_progress * 15)
                        else:
                            overall_progress = file_progress * 100
                            
                        percentage = round(overall_progress, 2)
                        
                        asyncio.run_coroutine_threadsafe(
                            update_progress_cb(percentage), 
                            loop
                        )

        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_path if os.path.exists(ffmpeg_path) else None,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en.*'],
            'subtitlesformat': 'vtt'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        return output_path

    @staticmethod
    async def run(url: str, job_id: uuid.UUID, update_progress_cb: Callable[[float], Awaitable[None]]) -> str:
        """
        Downloads a YouTube video asynchronously to avoid blocking the event loop.
        """
        os.makedirs("tmp", exist_ok=True)
        loop = asyncio.get_running_loop()
        return await asyncio.to_thread(DownloaderService._download_sync, url, job_id, update_progress_cb, loop)
