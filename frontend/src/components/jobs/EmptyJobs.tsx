import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Video } from 'lucide-react';

export function EmptyJobs() {
  const navigate = useNavigate();

  return (
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
  );
}
