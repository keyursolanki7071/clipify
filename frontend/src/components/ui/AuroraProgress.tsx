import React from 'react';

export function AuroraProgress() {
  return (
    <div className="w-full h-1 bg-surface-container-highest rounded-full mt-sm overflow-hidden">
      <div 
        className="h-full w-2/3 rounded-full" 
        style={{
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
