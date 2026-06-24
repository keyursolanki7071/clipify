import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Video, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export function JobsList() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/jobs/');
        if (response.ok) {
          const data = await response.json();
          setJobs(data);
        }
      } catch (err) {
        console.error("Error fetching jobs", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobs();
  }, []);

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'completed': return <CheckCircle size={16} className="text-green-400" />;
      case 'failed': return <AlertCircle size={16} className="text-red-400" />;
      default: return <Loader2 size={16} className="text-secondary animate-spin" />;
    }
  };

  return (
    <main className="flex-grow pt-[120px] pb-xxl px-md md:px-lg z-10 relative">
      <div className="max-w-container-max mx-auto flex flex-col gap-xl">
        <div className="flex items-center justify-between border-b border-white/5 pb-md">
          <div>
            <h1 className="font-headline-lg-mobile md:font-headline-lg text-on-surface mb-xs">Your Jobs History</h1>
            <p className="font-body-md text-on-surface-variant">View and manage all your generated shorts.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-xxl">
            <Loader2 className="animate-spin text-primary" size={32} />
          </div>
        ) : jobs.length === 0 ? (
          <div className="glass-panel p-xl rounded-2xl flex flex-col items-center justify-center text-center gap-md">
            <Video className="text-on-surface-variant opacity-50" size={48} />
            <h3 className="font-headline-md text-on-surface">No jobs found</h3>
            <p className="font-body-md text-on-surface-variant">You haven't generated any shorts yet.</p>
            <button 
              onClick={() => navigate('/')}
              className="mt-sm px-lg py-sm bg-primary/20 text-primary rounded-lg border border-primary/30 hover:bg-primary/30 transition-colors font-label-md"
            >
              Create New
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
            {jobs.map((job) => (
              <div 
                key={job.id} 
                onClick={() => navigate(job.status === 'completed' ? `/jobs/${job.id}` : `/processing?job_id=${job.id}`)}
                className="glass-card p-md rounded-2xl flex flex-col gap-md cursor-pointer hover:border-primary/50 transition-all hover:-translate-y-1 group relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                
                <div className="w-full aspect-video rounded-xl bg-surface-container-highest overflow-hidden relative">
                  <img src={job.video_thumbnail || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=300&auto=format&fit=crop"} alt="Thumbnail" className="w-full h-full object-cover opacity-80" />
                  <div className="absolute inset-0 bg-gradient-to-t from-surface/90 to-transparent"></div>
                  
                  {job.video_duration && (
                    <span className="absolute bottom-2 right-2 font-label-sm text-[10px] bg-black/80 px-1.5 py-0.5 rounded text-white backdrop-blur-sm">
                      {Math.floor(job.video_duration / 60)}:{(job.video_duration % 60).toString().padStart(2, '0')}
                    </span>
                  )}
                  
                  <div className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-1 bg-surface-container/90 backdrop-blur-md rounded-lg border border-white/10 font-label-sm text-[11px] uppercase tracking-wider text-on-surface">
                    {getStatusIcon(job.status)}
                    {job.status}
                  </div>
                </div>

                <div className="flex flex-col gap-xs z-10">
                  <h3 className="font-body-md font-semibold text-on-surface line-clamp-2 leading-snug">
                    {job.video_title || job.youtube_url}
                  </h3>
                  <div className="flex items-center gap-sm text-on-surface-variant font-label-sm text-[12px] mt-xs">
                    <span className="flex items-center gap-1"><Clock size={12} /> {(job.progress || 0).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
