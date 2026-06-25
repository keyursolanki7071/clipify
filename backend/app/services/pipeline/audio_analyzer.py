import librosa
import numpy as np
import asyncio
import subprocess
import tempfile
import os

class AudioAnalyzer:
    @staticmethod
    def _extract_energy_sync(video_path: str, sr: int = 16000, hop_length: int = 512) -> list[dict]:
        """
        Extracts Root Mean Square (RMS) energy from the audio track of the video.
        Returns a list of dictionaries with 'time' and 'energy'.
        """
        wav_path = None
        try:
            print("AudioAnalyzer: Starting extraction...")
            print(f"AudioAnalyzer: Creating temp wav file for {video_path}...")
            temp_fd, wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_fd)
            
            print(f"AudioAnalyzer: Running ffmpeg to extract audio to {wav_path}...")
            cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", str(sr), "-ac", "1", "-y", wav_path]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print("AudioAnalyzer: ffmpeg extraction complete.")

            print("AudioAnalyzer: Loading wav file with librosa...")
            y, sr = librosa.load(wav_path, sr=sr, mono=True)
            print("AudioAnalyzer: librosa load complete.")
            
            print("AudioAnalyzer: Calculating RMS energy...")
            # Calculate RMS energy
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
            
            # Convert frame indices to timestamps
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
            
            # Normalize energy to 0-1 range
            max_energy = np.max(rms) if np.max(rms) > 0 else 1.0
            normalized_rms = rms / max_energy
            
            # Downsample to 1 sample per second for easier alignment
            samples_per_sec = int(sr / hop_length)
            
            timeline = []
            for i in range(0, len(normalized_rms), samples_per_sec):
                window_energy = normalized_rms[i:i+samples_per_sec]
                avg_energy = float(np.mean(window_energy)) if len(window_energy) > 0 else 0.0
                time_sec = times[i]
                
                timeline.append({
                    "time": float(time_sec),
                    "energy": avg_energy
                })
                
            print(f"AudioAnalyzer: Extracted {len(timeline)} energy data points.")
            return timeline
            
        except Exception as e:
            print(f"AudioAnalyzer Error: {e}")
            return []
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass

    @staticmethod
    async def run(video_path: str) -> list[dict]:
        return await asyncio.to_thread(AudioAnalyzer._extract_energy_sync, video_path)
