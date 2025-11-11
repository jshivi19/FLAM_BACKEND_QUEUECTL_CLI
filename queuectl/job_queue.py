from typing import List, Optional
from .storage.job_storage import JobStorage
from .job import Job, JobState
from .config import get_config

class JobQueue:
    def __init__(self):
        self.storage = JobStorage()
    
    def enqueue(self, job_data: dict) -> Job:
        """Add a job to the queue"""
        config = get_config()
        if 'max_retries' not in job_data:
            job_data['max_retries'] = config.get('max_retries', 3)
        
        job = Job(**job_data)
        job.state = JobState.PENDING
        self.storage.add_job(job)
        return job
    
    def get_next_job(self) -> Optional[Job]:
        """Get the next available job to process"""
        return self.storage.get_next_pending_job()
    
    def update_job(self, job: Job):
        """Update job status"""
        self.storage.update_job(job)
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        return self.storage.get_job(job_id)
    
    def get_jobs_by_state(self, state: JobState) -> List[Job]:
        """Get jobs by state"""
        return self.storage.get_jobs_by_state(state)
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        return self.storage.get_all_jobs()
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        return self.storage.get_job_stats()
