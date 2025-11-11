from ..job_queue import JobQueue
import sys

def handle_enqueue(job_data):
    """Handle enqueue command"""
    queue = JobQueue()
    job = queue.enqueue(job_data)
    
    # Use ASCII checkmark for Windows compatibility
    checkmark = "OK" if sys.platform == 'win32' else "✓"
    
    print(f"{checkmark} Job enqueued: {job.id}")
    print(f"  Command: {job.command}")
    print(f"  Max retries: {job.max_retries}")
