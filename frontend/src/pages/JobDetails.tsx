import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { UserCircle } from 'lucide-react';
import { ClipCard } from '../components/shorts/ClipCard';
import { PreviewModal } from '../components/shorts/PreviewModal';

export function JobDetails() {
  const navigate = useNavigate();
  const { id: jobId } = useParams<{ id: string }>();

  const [selectedClip, setSelectedClip] = useState<any>(null);
  const [jobData, setJobData] = useState<any>(null);

  useEffect(() => {
    if (!jobId) {
      navigate('/');
      return;
    }

    const fetchJob = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
        if (response.ok) {
          const data = await response.json();
          setJobData(data);
        }
      } catch (err) {
        console.error("Error fetching job data", err);
      }
    };

    fetchJob();
  }, [jobId, navigate]);

  if (!jobData || !jobData.result_paths?.clips) {
    return (
      <main className="flex-grow pt-[120px] pb-xxl px-md md:px-lg z-10 relative flex items-center justify-center">
        <div className="text-white font-body-lg animate-pulse">Loading your shorts...</div>
      </main>
    );
  }

  const clips = jobData.result_paths.clips || [];

  return (
    <main className="flex-grow pt-[120px] pb-xxl px-md md:px-lg z-10 relative">
      <div className="max-w-container-max mx-auto flex flex-col gap-xl md:gap-xxl">
        
        <section className="relative w-full">
          <div className="absolute -inset-4 bg-primary/10 blur-[60px] rounded-[2rem] z-0 pointer-events-none"></div>
          <div className="relative z-10 glass-card rounded-2xl p-md md:p-lg flex flex-col md:flex-row gap-lg items-center md:items-stretch overflow-hidden">
            <div className="w-full md:w-[320px] lg:w-[400px] shrink-0 rounded-xl overflow-hidden relative group aspect-video bg-surface-container-high">
              <img src={jobData.video_thumbnail || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=600&auto=format&fit=crop"} alt="Video" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
              <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent"></div>
              {jobData.video_duration && (
                <div className="absolute bottom-2 right-2 bg-black/80 backdrop-blur-sm text-white px-1.5 py-0.5 rounded font-mono-code text-[12px]">
                  {Math.floor(jobData.video_duration / 60)}:{(jobData.video_duration % 60).toString().padStart(2, '0')}
                </div>
              )}
            </div>
            
            <div className="flex flex-col justify-center w-full flex-grow py-sm">
              <h1 className="font-headline-lg-mobile md:font-headline-lg text-on-surface mb-sm leading-tight">{jobData.video_title}</h1>
              <div className="flex items-center gap-sm text-on-surface-variant font-body-md text-sm mb-lg">
                <span className="flex items-center gap-1"><UserCircle size={16} /> YouTube</span>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-md mt-auto pt-md border-t border-white/10">
                <div>
                  <p className="font-label-sm text-[11px] text-on-surface-variant uppercase tracking-wider mb-1">Clips Found</p>
                  <p className="font-headline-lg-mobile text-[24px] text-primary font-bold">{clips.length}</p>
                </div>
                <div>
                  <p className="font-label-sm text-[11px] text-on-surface-variant uppercase tracking-wider mb-1">Viral Potential</p>
                  <p className="font-headline-lg-mobile text-[24px] text-on-surface font-bold">High</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div className="flex items-center justify-between border-b border-white/5 pb-md mt-lg">
          <h2 className="font-headline-lg-mobile md:font-headline-lg text-on-surface">Your AI Generated Shorts</h2>
        </div>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-gutter">
          {clips.map((clip: any, index: number) => (
            <ClipCard 
              key={index}
              score={100 - (clip.rank || index) * 5}
              title={clip.title}
              description={clip.explanation}
              videoUrl={clip.url}
              clipType={clip.clip_type}
              targetPlatform={clip.target_platform}
              confidence={clip.confidence}
              onPlay={() => setSelectedClip(clip)}
            />
          ))}
        </section>

        {selectedClip && (
          <PreviewModal 
            title={selectedClip.title}
            explanation={selectedClip.explanation}
            videoUrl={selectedClip.url}
            onClose={() => setSelectedClip(null)} 
          />
        )}
      </div>
    </main>
  );
}
