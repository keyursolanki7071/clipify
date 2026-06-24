import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { JobCard } from '../components/jobs/JobCard';
import { EmptyJobs } from '../components/jobs/EmptyJobs';

export function JobsList() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/jobs/');
        if (response.ok) {
          const data = await response.json();
          setJobs(data);
        }
      } catch (err) {
        console.error("Error fetching jobs", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobs();
  }, []);



  return (
    <main className="flex-grow pt-[120px] pb-xxl px-md md:px-lg z-10 relative">
      <div className="max-w-container-max mx-auto flex flex-col gap-xl">
        <div className="flex items-center justify-between border-b border-white/5 pb-md">
          <div>
            <h1 className="font-headline-lg-mobile md:font-headline-lg text-on-surface mb-xs">Your Jobs History</h1>
            <p className="font-body-md text-on-surface-variant">View and manage all your generated shorts.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-xxl">
            <Loader2 className="animate-spin text-primary" size={32} />
          </div>
        ) : jobs.length === 0 ? (
          <EmptyJobs />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
