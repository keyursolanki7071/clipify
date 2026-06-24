import React from 'react';
import { X, Download } from 'lucide-react';

interface PreviewModalProps {
  onClose: () => void;
  title: string;
}

export function PreviewModal({ onClose, title }: PreviewModalProps) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-md bg-background/80 backdrop-blur-sm">
      <div className="relative w-full max-w-5xl h-[80vh] bg-surface-container-highest rounded-2xl border border-white/10 flex flex-col md:flex-row overflow-hidden shadow-2xl">
        <div className="w-full md:w-1/2 bg-black flex items-center justify-center relative">
          <img src="https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=400&h=700&auto=format&fit=crop" className="h-full object-contain aspect-[9/16]" alt="Video Preview" />
          <button onClick={onClose} className="md:hidden absolute top-4 right-4 bg-black/50 text-white p-2 rounded-full"><X size={20} /></button>
        </div>
        <div className="w-full md:w-1/2 p-lg flex flex-col">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-semibold text-on-surface">{title}</h2>
            <button onClick={onClose} className="hidden md:flex text-on-surface-variant hover:text-white"><X size={24} /></button>
          </div>
          <div className="bg-surface-container-low p-4 rounded-xl border border-white/5 mb-4 text-on-surface-variant text-sm">
            <span className="text-primary font-semibold mb-2 block">AI Analysis</span>
            This clip contains a highly contrarian hook within the first 3 seconds...
          </div>
          <button className="mt-auto w-full bg-gradient-to-r from-primary to-inverse-primary text-on-primary py-3 rounded-xl font-bold flex items-center justify-center gap-2">
            <Download size={20} /> Download HD
          </button>
        </div>
      </div>
    </div>
  );
}
