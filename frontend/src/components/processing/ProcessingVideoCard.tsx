import React from 'react';
import { User } from 'lucide-react';

interface ProcessingVideoCardProps {
  jobData: any;
}

export function ProcessingVideoCard({ jobData }: ProcessingVideoCardProps) {
  if (!jobData?.video_title) return null;
  
  return (
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
  );
}
