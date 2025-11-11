#!/usr/bin/env python3
"""
Helper script to enqueue jobs (Windows-friendly)
Usage: python enqueue_job.py <job_id> <command> [max_retries]
"""

import sys
import subprocess
import json

def enqueue_job(job_id, command, max_retries=3):
    """Enqueue a job using queuectl"""
    job = {
        "id": job_id,
        "command": command,
        "max_retries": max_retries
    }
    
    job_json = json.dumps(job)
    cmd = ['queuectl', 'enqueue', job_json]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    if len(sys.argv) < 3:
        print("Usage: python enqueue_job.py <job_id> <command> [max_retries]")
        print("\nExamples:")
        print('  python enqueue_job.py job1 "echo Hello World"')
        print('  python enqueue_job.py job2 "sleep 2" 5')
        sys.exit(1)
    
    job_id = sys.argv[1]
    command = sys.argv[2]
    max_retries = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    sys.exit(enqueue_job(job_id, command, max_retries))

if __name__ == '__main__':
    main()
