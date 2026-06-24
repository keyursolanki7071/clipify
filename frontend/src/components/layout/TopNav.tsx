import React from 'react';
import { Link } from 'react-router-dom';
import { PlaySquare, Clipboard } from 'lucide-react';

export function TopNav() {
  return (
    <nav className="bg-surface/50 dark:bg-surface/50 backdrop-blur-xl text-primary font-headline-lg text-headline-lg fixed top-0 w-full z-50 border-b border-white/10 shadow-[0_0_20px_rgba(208,188,255,0.1)]">
      <div className="flex justify-between items-center px-lg h-xxl max-w-container-max mx-auto">
        <Link to="/" className="flex items-center gap-sm">
          <PlaySquare className="text-primary" size={32} />
          <span className="font-display-xl text-headline-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary cursor-pointer hover:opacity-80 transition-opacity">
            Clipify AI
          </span>
        </Link>
      </div>
    </nav>
  );
}
