import React from 'react';
import { Check, Loader2 } from 'lucide-react';
import { AuroraProgress } from '../ui/AuroraProgress';

export type StepStatus = 'completed' | 'active' | 'upcoming';

interface ProcessingStepProps {
  status: StepStatus;
  title: string;
  progress?: number;
}

export function ProcessingStep({ status, title, progress }: ProcessingStepProps) {
  const getOpacity = () => {
    if (status === 'completed') return 'opacity-50';
    if (status === 'upcoming') return 'opacity-30';
    return '';
  };

  return (
    <div className={`flex items-start gap-md relative z-10 ${getOpacity()}`}>
      <div className={`w-8 h-8 rounded-full border flex items-center justify-center shrink-0 mt-1 ${
        status === 'active' 
          ? 'bg-primary/20 border-primary' 
          : 'bg-surface-container-highest border-white/10'
      }`}>
        {status === 'completed' && <Check className="text-on-surface-variant" size={16} />}
        {status === 'active' && <Loader2 className="text-primary animate-spin" size={16} />}
        {status === 'upcoming' && <span className="w-2 h-2 rounded-full bg-on-surface-variant"></span>}
      </div>
      <div className="flex-col pt-1 w-full">
        <span className={`font-body-md ${status === 'active' ? 'text-primary font-medium' : 'text-on-surface-variant'}`}>
          {title}
        </span>
        {status === 'active' && <AuroraProgress progress={progress} />}
      </div>
    </div>
  );
}
