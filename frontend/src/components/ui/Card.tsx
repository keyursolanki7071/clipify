import React from 'react';

export function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`glass-card rounded-2xl p-xl border border-white/5 relative overflow-hidden group ${className}`}>
      {children}
    </div>
  );
}
