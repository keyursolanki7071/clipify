import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Chip } from '../components/ui/Chip';
import { Card } from '../components/ui/Card';
import { Sparkles, Link, Zap, Mic, MessageSquare, BookOpen, Dumbbell } from 'lucide-react';

export function Home() {
  const navigate = useNavigate();

  const handleGenerate = () => {
    navigate('/processing');
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
        >
          <Button onClick={handleGenerate}>
            <Zap size={20} />
            Generate Shorts
          </Button>
        </Input>

        <div className="flex flex-col items-center gap-sm">
          <span className="font-label-sm text-label-sm text-outline uppercase tracking-wider">Or try an example</span>
          <div className="flex flex-wrap justify-center gap-sm">
            <Chip icon={<Mic size={16} />}>Podcast</Chip>
            <Chip icon={<MessageSquare size={16} />}>Interview</Chip>
            <Chip icon={<BookOpen size={16} />}>Educational Video</Chip>
            <Chip icon={<Dumbbell size={16} />} className="hidden sm:flex">Motivational Video</Chip>
          </div>
        </div>
      </div>

      <Card className="w-full max-w-4xl p-xl flex flex-col items-center justify-center text-center gap-lg min-h-[400px]">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_70%)] opacity-50 z-0"></div>
        <div className="relative z-10 flex flex-col items-center">
          <div className="relative w-32 h-32 mb-md flex items-center justify-center">
            <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl animate-pulse"></div>
            <div className="absolute inset-2 bg-gradient-to-tr from-surface to-surface-container rounded-full border border-primary/30 flex items-center justify-center shadow-[0_0_30px_rgba(208,188,255,0.1)]">
              <Sparkles size={48} className="text-primary opacity-80" />
            </div>
          </div>
          <h3 className="font-headline-lg text-[24px] text-on-surface font-semibold mb-xs">Awaiting Input</h3>
          <p className="font-body-md text-on-surface-variant max-w-md mx-auto">
            Paste a YouTube link above to create your first viral shorts. Our AI will analyze the content and extract the highest-performing clips automatically.
          </p>
        </div>
      </Card>
    </main>
  );
}
