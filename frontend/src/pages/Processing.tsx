import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, User, Timer } from 'lucide-react';
import { ProcessingStep } from '../components/processing/ProcessingStep';

export function Processing() {
  const navigate = useNavigate();

  useEffect(() => {
    // Simulate processing time
    const timer = setTimeout(() => {
      navigate('/shorts');
    }, 5000);
    return () => clearTimeout(timer);
  }, [navigate]);

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

        <div className="glass-panel rounded-xl p-md flex items-center gap-md bg-surface-container-highest/50">
          <div className="w-24 h-16 rounded-lg overflow-hidden relative shrink-0 border border-white/10">
            <img src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=300&auto=format&fit=crop" alt="Thumbnail" className="w-full h-full object-cover opacity-80" />
            <div className="absolute inset-0 bg-gradient-to-t from-surface/80 to-transparent"></div>
            <span className="absolute bottom-1 right-1 font-label-sm text-[10px] bg-surface/90 px-1 py-0.5 rounded text-on-surface backdrop-blur-sm">12:45</span>
          </div>
          <div className="flex-col overflow-hidden">
            <h3 className="font-body-md font-medium text-on-surface truncate">The Future of AI in Design</h3>
            <p className="font-label-sm text-[11px] text-on-surface-variant truncate mt-1 flex items-center gap-1">
              <User size={14} /> Tech Today
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-md relative">
          <div className="absolute left-[15px] top-[20px] bottom-[20px] w-[2px] bg-surface-container-highest z-0"></div>
          
          <ProcessingStep status="completed" title="Downloading Video" />
          <ProcessingStep status="active" title="Understanding Content" />
          <ProcessingStep status="upcoming" title="Finding Viral Moments" />
        </div>

        <div className="pt-md border-t border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-sm">
            <Timer className="text-secondary" size={20} />
            <span className="font-mono-code text-[14px] text-secondary">Estimated completion: 5 seconds</span>
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
