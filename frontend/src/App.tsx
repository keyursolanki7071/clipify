import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TopNav } from './components/layout/TopNav';
import { Home } from './pages/Home';
import { Processing } from './pages/Processing';
import { JobDetails } from './pages/JobDetails';
import { JobsList } from './pages/JobsList';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col relative selection:bg-primary/30 selection:text-primary">
        {/* Atmospheric Aurora Background */}
        <div className="aurora-bg">
          <div className="aurora-blob blob-1"></div>
          <div className="aurora-blob blob-2"></div>
        </div>

        <TopNav />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/processing" element={<Processing />} />
          <Route path="/jobs" element={<JobsList />} />
          <Route path="/jobs/:id" element={<JobDetails />} />
        </Routes>

        <footer className="bg-surface/50 backdrop-blur-md text-primary font-label-sm text-label-sm w-full py-xl border-t border-white/5 relative z-10 mt-auto">
          <div className="flex flex-col md:flex-row justify-between items-center px-lg max-w-container-max mx-auto gap-md">
            <span className="text-label-sm font-bold text-on-surface">© 2024 Clipify AI. Made with AI</span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
