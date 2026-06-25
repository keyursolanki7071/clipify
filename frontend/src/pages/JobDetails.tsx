import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { UserCircle } from 'lucide-react';
import { ClipCard } from '../components/shorts/ClipCard';
import { PreviewModal } from '../components/shorts/PreviewModal';
import { JobVideoHeader } from '../components/jobs/JobVideoHeader';

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
        
        <JobVideoHeader jobData={jobData} clipsCount={clips.length} />

        <div className="flex items-center justify-between border-b border-white/5 pb-md mt-lg">
          <h2 className="font-headline-lg-mobile md:font-headline-lg text-on-surface">Your AI Generated Shorts</h2>
          <button 
            onClick={async () => {
              try {
                await fetch(`http://localhost:8000/api/v1/jobs/${jobId}/restart`, { method: 'POST' });
                navigate(`/processing?job_id=${jobId}`);
              } catch (err) {
                console.error(err);
              }
            }}
            className="px-4 py-2 bg-surface-container-high hover:bg-surface-container-highest border border-white/10 rounded-xl font-label-md text-on-surface-variant hover:text-white transition-colors"
          >
            Re-run AI
          </button>
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
            caption={selectedClip.social_media_caption || `${selectedClip.title}\n\n#shorts #viral`}
            onClose={() => setSelectedClip(null)} 
          />
        )}
      </div>
    </main>
  );
}
