import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, User, Timer } from 'lucide-react';
import { ProcessingStep } from '../components/processing/ProcessingStep';

export function Processing() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const jobId = queryParams.get('job_id');
  
  const [jobStatus, setJobStatus] = useState<string>('pending');
  const [jobData, setJobData] = useState<any>(null);

  useEffect(() => {
    if (!jobId) {
      navigate('/');
      return;
    }

    const pollJob = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
        if (response.ok) {
          const data = await response.json();
          setJobData(data);
          setJobStatus(data.status);
          
          if (data.status === 'completed') {
            navigate(`/shorts?job_id=${jobId}`);
          }
        }
      } catch (err) {
        console.error("Error polling job status", err);
      }
    };

    // Poll immediately, then every 2 seconds
    pollJob();
    const interval = setInterval(pollJob, 2000);
    
    return () => clearInterval(interval);
  }, [jobId, navigate]);

  const getStepStatus = (stepName: string) => {
    const order = ['pending', 'downloading', 'transcribing', 'analyzing', 'clipping', 'completed'];
    let currentStatus = jobStatus;
    if (currentStatus === 'pending') currentStatus = 'downloading'; // visual fallback
    
    const currentIndex = order.indexOf(currentStatus);
    const stepIndex = order.indexOf(stepName);
    
    if (currentIndex > stepIndex) return 'completed';
    if (currentIndex === stepIndex) return 'active';
    return 'upcoming';
  };

  return (
    <main className="relative z-10 flex flex-col items-center justify-center min-h-screen p-md md:p-xl flex-grow pt-[120px]">
      <div className="bg-surface-container-high/80 backdrop-blur-xl border border-white/10 shadow-[0_0_40px_rgba(139,92,246,0.15)] rounded-[24px] w-full max-w-[600px] p-lg md:p-xl flex flex-col gap-xl relative overflow-hidden">
        
        <div className="text-center space-y-sm">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-surface-container-highest border border-white/10 mb-md relative">
            <Sparkles className="text-primary animate-pulse" size={32} />
          </div>
          <h1 className="font-headline-lg-mobile md:font-headline-lg text-on-surface text-shimmer font-bold">Extracting Viral Magic</h1>
          <p className="font-body-md text-on-surface-variant">Our AI is analyzing your video to find the best moments.</p>
        </div>

        {jobData?.video_title && (
        <div className="glass-panel rounded-xl p-md flex items-center gap-md bg-surface-container-highest/50">
          <div className="w-24 h-16 rounded-lg overflow-hidden relative shrink-0 border border-white/10">
            <img src={jobData.video_thumbnail || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=300&auto=format&fit=crop"} alt="Thumbnail" className="w-full h-full object-cover opacity-80" />
            <div className="absolute inset-0 bg-gradient-to-t from-surface/80 to-transparent"></div>
            {jobData.video_duration && (
              <span className="absolute bottom-1 right-1 font-label-sm text-[10px] bg-surface/90 px-1 py-0.5 rounded text-on-surface backdrop-blur-sm">
                {Math.floor(jobData.video_duration / 60)}:{(jobData.video_duration % 60).toString().padStart(2, '0')}
              </span>
            )}
          </div>
          <div className="flex-col overflow-hidden">
            <h3 className="font-body-md font-medium text-on-surface truncate">{jobData.video_title}</h3>
            <p className="font-label-sm text-[11px] text-on-surface-variant truncate mt-1 flex items-center gap-1">
              <User size={14} /> YouTube
            </p>
          </div>
        </div>
        )}

        <div className="flex flex-col gap-md relative">
          <div className="absolute left-[15px] top-[20px] bottom-[20px] w-[2px] bg-surface-container-highest z-0"></div>
          
          <ProcessingStep 
            status={getStepStatus('downloading')} 
            title={`Downloading Video${jobStatus === 'downloading' && jobData?.progress ? ` (${jobData.progress}%)` : ''}`} 
            progress={jobStatus === 'downloading' ? jobData?.progress : undefined}
          />
          <ProcessingStep status={getStepStatus('transcribing')} title="Transcribing Audio" />
          <ProcessingStep status={getStepStatus('analyzing')} title="Finding Viral Moments" />
          <ProcessingStep status={getStepStatus('clipping')} title="Cutting & Captioning" />
        </div>

        <div className="pt-md border-t border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-sm">
            <Timer className="text-secondary" size={20} />
            <span className="font-mono-code text-[14px] text-secondary">Status: {jobStatus.toUpperCase()}</span>
          </div>
          <button 
            onClick={() => navigate('/')}
            className="px-4 py-2 rounded-lg border border-white/10 text-on-surface-variant font-label-sm text-label-sm hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </main>
  );
}
