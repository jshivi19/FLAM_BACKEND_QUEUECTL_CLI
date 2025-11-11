#!/usr/bin/env python3
"""
Quick demo script that works on all platforms
Directly uses the Python API instead of CLI
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from queuectl.job_queue import JobQueue
from queuectl.config import get_config

def main():
    print("=" * 70)
    print("QUEUECTL QUICK DEMO (Direct API)")
    print("=" * 70)
    
    # Configure
    print("\n1. Configuring system...")
    config = get_config()
    config.set('max_retries', 3)
    config.set('backoff_base', 2)
    print("✓ Configuration set: max_retries=3, backoff_base=2")
    
    # Create queue
    queue = JobQueue()
    
    # Enqueue jobs
    print("\n2. Enqueuing jobs...")
    jobs = [
        {"id": "demo1", "command": "echo Job 1 completed"},
        {"id": "demo2", "command": "echo Job 2 completed"},
        {"id": "demo3", "command": "timeout 2 >nul & echo Job 3 done" if sys.platform == 'win32' else "sleep 2 && echo Job 3 done"},
        {"id": "fail_job", "command": "exit 1", "max_retries": 2}
    ]
    
    for job_data in jobs:
        job = queue.enqueue(job_data)
        print(f"✓ Enqueued: {job.id} - {job.command[:40]}...")
    
    # Show status
    print("\n3. Current status:")
    stats = queue.get_stats()
    print(f"  Pending: {stats['pending']}")
    print(f"  Total: {sum(stats.values())}")
    
    print("\n" + "=" * 70)
    print("Jobs are ready! Now start workers:")
    print("\n  queuectl worker start")
    print("\nOr start multiple workers:")
    print("\n  queuectl worker start --count 2")
    print("\nThen check status:")
    print("\n  queuectl status")
    print("  queuectl list")
    print("=" * 70)

if __name__ == '__main__':
    main()
