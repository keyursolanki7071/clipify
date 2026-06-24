import React, { useState } from 'react';
import { X, Download, Copy, Check } from 'lucide-react';

interface PreviewModalProps {
  onClose: () => void;
  title: string;
  explanation: string;
  videoUrl: string;
  caption: string;
}

export function PreviewModal({ onClose, title, explanation, videoUrl, caption }: PreviewModalProps) {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(caption);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-md bg-background/80 backdrop-blur-sm">
      <div className="relative w-full max-w-5xl h-[80vh] bg-surface-container-highest rounded-2xl border border-white/10 flex flex-col md:flex-row overflow-hidden shadow-2xl">
        <div className="w-full md:w-1/2 bg-black flex items-center justify-center relative">
          <video src={videoUrl} controls className="h-full object-contain aspect-[9/16]" />
          <button onClick={onClose} className="md:hidden absolute top-4 right-4 bg-black/50 text-white p-2 rounded-full"><X size={20} /></button>
        </div>
        <div className="w-full md:w-1/2 p-lg flex flex-col">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-semibold text-on-surface">{title}</h2>
            <button onClick={onClose} className="hidden md:flex text-on-surface-variant hover:text-white"><X size={24} /></button>
          </div>
          <div className="bg-surface-container-low p-4 rounded-xl border border-white/5 mb-4 text-on-surface-variant text-sm flex-grow overflow-y-auto">
            <span className="text-primary font-semibold mb-2 block">AI Analysis</span>
            <p className="mb-4">{explanation}</p>
            
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="flex items-center justify-between mb-2">
                <span className="text-primary font-semibold block">Social Media Caption</span>
                <button 
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-[11px] bg-white/5 hover:bg-white/10 px-2 py-1 rounded border border-white/10 transition-colors"
                >
                  {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="bg-black/30 p-3 rounded-lg font-mono-code text-[12px] whitespace-pre-wrap text-on-surface/80">
                {caption}
              </div>
            </div>
          </div>
          <button 
            onClick={() => {
              const a = document.createElement('a');
              a.href = videoUrl;
              a.download = `clip-${title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.mp4`;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
            }}
            className="mt-auto w-full bg-gradient-to-r from-primary to-inverse-primary text-on-primary py-3 rounded-xl font-bold flex items-center justify-center gap-2"
          >
            <Download size={20} /> Download HD
          </button>
        </div>
      </div>
    </div>
  );
}
