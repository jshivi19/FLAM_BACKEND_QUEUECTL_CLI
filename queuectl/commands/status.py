from ..job_queue import JobQueue
from ..worker_manager import WorkerManager

def show_status():
    """Show queue status"""
    queue = JobQueue()
    manager = WorkerManager()
    
    stats = queue.get_stats()
    active_workers = manager.get_active_workers()
    
    print("=" * 50)
    print("QUEUECTL STATUS")
    print("=" * 50)
    print(f"\nActive Workers: {len(active_workers)}")
    if active_workers:
        print(f"  PIDs: {', '.join(map(str, active_workers))}")
    
    print(f"\nJob Statistics:")
    print(f"  Pending:    {stats.get('pending', 0)}")
    print(f"  Processing: {stats.get('processing', 0)}")
    print(f"  Completed:  {stats.get('completed', 0)}")
    print(f"  Failed:     {stats.get('failed', 0)}")
    print(f"  Dead (DLQ): {stats.get('dead', 0)}")
    print(f"  Total:      {sum(stats.values())}")
    print("=" * 50)
