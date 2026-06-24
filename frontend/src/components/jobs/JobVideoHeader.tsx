import React from 'react';
import { UserCircle } from 'lucide-react';

interface JobVideoHeaderProps {
  jobData: any;
  clipsCount: number;
}

export function JobVideoHeader({ jobData, clipsCount }: JobVideoHeaderProps) {
  return (
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
              <p className="font-headline-lg-mobile text-[24px] text-primary font-bold">{clipsCount}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
