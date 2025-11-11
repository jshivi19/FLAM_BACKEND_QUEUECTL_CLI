import json
import os
import sys
from pathlib import Path
from typing import List, Optional
from ..job import Job, JobState
from ..config import get_config

# Platform-specific locking
if sys.platform == 'win32':
    import msvcrt
    
    def _lock_file(file_handle):
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
    
    def _unlock_file(file_handle):
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    
    def _lock_file(file_handle):
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX)
    
    def _unlock_file(file_handle):
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)

class JobStorage:
    def __init__(self):
        self.data_dir = get_config().get_data_dir()
        self.jobs_file = self.data_dir / "jobs.json"
        self.lock_file = self.data_dir / "jobs.lock"
        self._ensure_files()
    
    def _ensure_files(self):
        if not self.jobs_file.exists():
            self._write_jobs([])
    
    def _acquire_lock(self, file_handle):
        """Acquire exclusive lock on file"""
        try:
            _lock_file(file_handle)
        except:
            pass  # Best effort locking
    
    def _release_lock(self, file_handle):
        """Release lock on file"""
        try:
            _unlock_file(file_handle)
        except:
            pass  # Best effort locking
    
    def _read_jobs(self) -> List[Job]:
        """Read all jobs from storage with locking"""
        with open(self.jobs_file, 'r') as f:
            self._acquire_lock(f)
            try:
                data = json.load(f)
                return [Job.from_dict(job_data) for job_data in data]
            finally:
                self._release_lock(f)
    
    def _write_jobs(self, jobs: List[Job]):
        """Write all jobs to storage with locking"""
        with open(self.jobs_file, 'w') as f:
            self._acquire_lock(f)
            try:
                json.dump([job.to_dict() for job in jobs], f, indent=2)
            finally:
                self._release_lock(f)
    
    def add_job(self, job: Job):
        """Add a new job"""
        jobs = self._read_jobs()
        jobs.append(job)
        self._write_jobs(jobs)
    
    def update_job(self, updated_job: Job):
        """Update an existing job"""
        jobs = self._read_jobs()
        for i, job in enumerate(jobs):
            if job.id == updated_job.id:
                jobs[i] = updated_job
                break
        self._write_jobs(jobs)
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        jobs = self._read_jobs()
        for job in jobs:
            if job.id == job_id:
                return job
        return None
    
    def get_next_pending_job(self) -> Optional[Job]:
        """Get the next pending job and mark it as processing"""
        jobs = self._read_jobs()
        for job in jobs:
            if job.state == JobState.PENDING:
                job.mark_processing()
                self._write_jobs(jobs)
                return job
        return None
    
    def get_jobs_by_state(self, state: JobState) -> List[Job]:
        """Get all jobs with a specific state"""
        jobs = self._read_jobs()
        return [job for job in jobs if job.state == state]
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        return self._read_jobs()
    
    def get_job_stats(self) -> dict:
        """Get statistics about jobs"""
        jobs = self._read_jobs()
        stats = {state.value: 0 for state in JobState}
        for job in jobs:
            stats[job.state.value] += 1
        return stats
