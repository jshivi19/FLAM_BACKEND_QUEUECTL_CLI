from ..job_queue import JobQueue
from ..job import JobState

import sys

def list_dlq():
    """List jobs in Dead Letter Queue"""
    queue = JobQueue()
    jobs = queue.get_jobs_by_state(JobState.DEAD)
    
    print("\nDead Letter Queue:")
    
    if not jobs:
        print("  No jobs in DLQ")
        return
    
    print(f"\n{'ID':<15} {'Command':<30} {'Attempts':<10} {'Created':<20}")
    print("-" * 80)
    
    for job in jobs:
        command = job.command[:27] + "..." if len(job.command) > 30 else job.command
        created = job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{job.id:<15} {command:<30} {job.attempts:<10} {created:<20}")

def retry_job(job_id):
    """Retry a job from DLQ"""
    queue = JobQueue()
    job = queue.get_job(job_id)
    
    if not job:
        print(f"Job not found: {job_id}")
        return
    
    if job.state != JobState.DEAD:
        print(f"Job {job_id} is not in DLQ (current state: {job.state.value})")
        return
    
    job.state = JobState.PENDING
    job.attempts = 0
    queue.update_job(job)
    
    checkmark = "OK" if sys.platform == 'win32' else "✓"
    print(f"{checkmark} Job {job_id} moved back to pending queue")
