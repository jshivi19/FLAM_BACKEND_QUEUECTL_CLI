from ..job_queue import JobQueue

def handle_enqueue(job_data):
    """Handle enqueue command"""
    queue = JobQueue()
    job = queue.enqueue(job_data)
    print(f"✓ Job enqueued: {job.id}")
    print(f"  Command: {job.command}")
    print(f"  Max retries: {job.max_retries}")
