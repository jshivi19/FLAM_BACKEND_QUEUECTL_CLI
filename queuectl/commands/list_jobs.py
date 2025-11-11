from ..job_queue import JobQueue
from ..job import JobState

def show_list(state_filter=None):
    """List jobs, optionally filtered by state"""
    queue = JobQueue()
    
    if state_filter:
        try:
            state = JobState(state_filter)
            jobs = queue.get_jobs_by_state(state)
            print(f"\nJobs with state: {state_filter}")
        except ValueError:
            print(f"Invalid state: {state_filter}")
            print(f"Valid states: {', '.join([s.value for s in JobState])}")
            return
    else:
        jobs = queue.get_all_jobs()
        print("\nAll jobs:")
    
    if not jobs:
        print("  No jobs found")
        return
    
    print(f"\n{'ID':<15} {'Command':<30} {'State':<12} {'Attempts':<10} {'Created':<20}")
    print("-" * 90)
    
    for job in jobs:
        command = job.command[:27] + "..." if len(job.command) > 30 else job.command
        created = job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{job.id:<15} {command:<30} {job.state.value:<12} {job.attempts}/{job.max_retries:<7} {created:<20}")
