import React from 'react';
import { Flame, Play, Download, Edit3, Share2 } from 'lucide-react';

interface ClipCardProps {
  score: number;
  title: string;
  description: string;
  videoUrl: string;
  clipType?: string;
  targetPlatform?: string;
  confidence?: string;
  onPlay: () => void;
}

export function ClipCard({ score, title, description, videoUrl, clipType, targetPlatform, confidence, onPlay }: ClipCardProps) {
  return (
    <article className="clip-card group relative bg-surface-container-low rounded-xl flex flex-col overflow-hidden transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_15px_40px_rgba(208,188,255,0.15)] col-span-1">
      <div className="relative w-full aspect-[9/16] bg-surface-bright overflow-hidden">
        <video 
          src={videoUrl} 
          preload="metadata" 
          muted 
          loop 
          playsInline
          className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" 
          onMouseEnter={(e) => (e.target as HTMLVideoElement).play().catch(() => {})} 
          onMouseLeave={(e) => { (e.target as HTMLVideoElement).pause(); (e.target as HTMLVideoElement).currentTime = 0; }} 
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent opacity-90"></div>
        
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-gradient-to-r from-[#FF4500] to-[#FF8C00] text-white font-label-sm text-[11px] font-bold shadow-lg">
            <Flame size={12} /> Score: {score}
          </div>
          {confidence && (
            <div className={`px-2 py-1 rounded-md text-white font-label-sm text-[10px] font-bold shadow-lg uppercase ${
              confidence === 'high' ? 'bg-green-500/90' : confidence === 'medium' ? 'bg-yellow-500/90' : 'bg-red-500/90'
            }`}>
              {confidence} CONFIDENCE
            </div>
          )}
          {clipType && (
            <div className="px-2 py-1 rounded-md bg-primary/90 text-on-primary font-label-sm text-[10px] font-bold shadow-lg capitalize">
              {clipType.replace('_', ' ')}
            </div>
          )}
        </div>
        
        <button onClick={onPlay} className="absolute inset-0 m-auto w-12 h-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:bg-white/20 z-10">
          <Play size={24} fill="currentColor" />
        </button>
      </div>
      
      <div className="relative z-10 p-4 flex flex-col flex-grow bg-surface-container-lowest/80 backdrop-blur-xl">
        <h3 className="font-body-md text-base font-semibold text-on-surface leading-tight mb-2 line-clamp-2">{title}</h3>
        <p className="font-body-md text-xs text-on-surface-variant line-clamp-2 mb-4 flex-grow">{description}</p>
        
        <div className="flex items-center gap-2 mt-auto pt-2 border-t border-white/5">
          <button className="flex-grow flex items-center justify-center gap-1 bg-primary text-on-primary py-2 rounded-lg font-label-sm text-[12px] font-semibold hover:bg-primary-fixed transition-colors">
            <Download size={14} /> Download
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/10 text-on-surface-variant hover:text-white transition-colors">
            <Edit3 size={14} />
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/10 text-on-surface-variant hover:text-white transition-colors">
            <Share2 size={14} />
          </button>
        </div>
      </div>
    </article>
  );
}
