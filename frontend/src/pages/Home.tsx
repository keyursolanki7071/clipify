import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Chip } from '../components/ui/Chip';
import { Card } from '../components/ui/Card';
import { Sparkles, Link, Zap } from 'lucide-react';

export function Home() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleGenerate = async () => {
    if (!url) return;
    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ youtube_url: url }),
      });
      if (response.ok) {
        const data = await response.json();
        navigate(`/processing?job_id=${data.id}`);
      } else {
        console.error("Failed to start job");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="flex-grow flex flex-col items-center justify-center pt-[120px] pb-xxl px-md md:px-xl max-w-container-max mx-auto w-full relative z-10">
      <div className="w-full max-w-3xl flex flex-col items-center text-center gap-md mb-xl mt-lg">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary font-label-sm text-label-sm mb-sm glass-panel">
          <Sparkles size={14} />
          <span>Powered by Advanced AI</span>
        </div>
        <h1 className="font-display-xl text-display-xl text-on-surface md:text-[72px] leading-tight md:leading-[80px] tracking-tight">
          Turn Any YouTube Video <br className="hidden md:block" /> Into <span className="text-shimmer font-bold">Viral Shorts</span>
        </h1>
        <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl mx-auto mt-sm">
          Paste a YouTube link and let AI automatically find the most engaging moments, crop faces, and add viral captions in seconds.
        </p>
      </div>

      <div className="w-full max-w-3xl flex flex-col gap-lg mb-xxl relative z-20">
        <Input 
          icon={<Link size={20} />} 
          placeholder="https://youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={isSubmitting}
        >
          <Button onClick={handleGenerate} disabled={isSubmitting || !url}>
            <Zap size={20} />
            {isSubmitting ? 'Starting...' : 'Generate Shorts'}
          </Button>
        </Input>
      </div>
    </main>
  );
}
