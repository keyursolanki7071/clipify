import React from 'react';

interface AuroraProgressProps {
  progress?: number;
}

export function AuroraProgress({ progress }: AuroraProgressProps) {
  const widthPercent = progress !== undefined ? `${Math.max(0, Math.min(100, progress))}%` : '66.66%';
  
  return (
    <div className="w-full h-1 bg-surface-container-highest rounded-full mt-sm overflow-hidden">
      <div 
        className="h-full rounded-full transition-all duration-300 ease-out" 
        style={{
          width: widthPercent,
          background: 'linear-gradient(90deg, #d0bcff, #adc6ff, #a078ff, #d0bcff)',
          backgroundSize: '300% 100%',
          animation: 'move-aurora 3s linear infinite'
        }}
      />
      <style>{`
        @keyframes move-aurora {
          0% { background-position: 100% 0; }
          100% { background-position: 0 0; }
        }
      `}</style>
    </div>
  );
}
