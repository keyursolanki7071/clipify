import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface JobCardProps {
  job: any;
}

export function JobCard({ job }: JobCardProps) {
  const navigate = useNavigate();

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'completed': return <CheckCircle size={16} className="text-green-400" />;
      case 'failed': return <AlertCircle size={16} className="text-red-400" />;
      default: return <Loader2 size={16} className="text-secondary animate-spin" />;
    }
  };

  const handleClick = () => {
    navigate(job.status === 'completed' ? `/jobs/${job.id}` : `/processing?job_id=${job.id}`);
  };

  return (
    <div 
      onClick={handleClick}
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
  );
}
