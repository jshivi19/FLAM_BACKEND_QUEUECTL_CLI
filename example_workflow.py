#!/usr/bin/env python3
"""
Example workflow demonstrating queuectl capabilities
This script shows a realistic use case: processing a batch of files
"""

import subprocess
import time
import json

def run(cmd):
    """Execute a queuectl command"""
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True)
    time.sleep(0.3)

def main():
    print("=" * 70)
    print("QUEUECTL EXAMPLE WORKFLOW")
    print("Scenario: Batch file processing with error handling")
    print("=" * 70)
    
    # Step 1: Configure the system
    print("\n" + "=" * 70)
    print("STEP 1: Configure retry behavior")
    print("=" * 70)
    run('queuectl config set max_retries 3')
    run('queuectl config set backoff_base 2')
    
    # Step 2: Enqueue various types of jobs
    print("\n" + "=" * 70)
    print("STEP 2: Enqueue batch processing jobs")
    print("=" * 70)
    
    jobs = [
        {
            "id": "process_file_1",
            "command": "echo Processing file1.txt && sleep 1 && echo Done",
            "max_retries": 3
        },
        {
            "id": "process_file_2",
            "command": "echo Processing file2.txt && sleep 1 && echo Done",
            "max_retries": 3
        },
        {
            "id": "process_file_3",
            "command": "echo Processing file3.txt && sleep 2 && echo Done",
            "max_retries": 3
        },
        {
            "id": "corrupted_file",
            "command": "echo Attempting to process corrupted.txt && exit 1",
            "max_retries": 2
        },
        {
            "id": "large_file",
            "command": "echo Processing large_file.txt && sleep 3 && echo Completed",
            "max_retries": 3
        }
    ]
    
    for job in jobs:
        job_json = json.dumps(job).replace('"', '\\"')
        run(f'queuectl enqueue "{job_json}"')
    
    # Step 3: Check initial status
    print("\n" + "=" * 70)
    print("STEP 3: Check queue status")
    print("=" * 70)
    run('queuectl status')
    
    # Step 4: List pending jobs
    print("\n" + "=" * 70)
    print("STEP 4: View pending jobs")
    print("=" * 70)
    run('queuectl list --state pending')
    
    # Step 5: Instructions for processing
    print("\n" + "=" * 70)
    print("STEP 5: Process the jobs")
    print("=" * 70)
    print("\nTo process these jobs, open a new terminal and run:")
    print("\n  queuectl worker start --count 2")
    print("\nThis will start 2 workers to process jobs in parallel.")
    print("Press Ctrl+C in the worker terminal to stop when done.")
    
    # Step 6: Monitoring instructions
    print("\n" + "=" * 70)
    print("STEP 6: Monitor progress")
    print("=" * 70)
    print("\nWhile workers are running, you can monitor progress:")
    print("\n  queuectl status              # Overall status")
    print("  queuectl list                # All jobs")
    print("  queuectl list --state completed  # Completed jobs")
    print("  queuectl list --state failed     # Failed jobs")
    
    # Step 7: DLQ handling
    print("\n" + "=" * 70)
    print("STEP 7: Handle failed jobs")
    print("=" * 70)
    print("\nAfter workers finish, check for failed jobs:")
    print("\n  queuectl dlq list            # View DLQ")
    print("  queuectl dlq retry <job_id>  # Retry a failed job")
    
    # Summary
    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)
    print("""
This example demonstrates:
✓ Configuration management
✓ Batch job enqueuing
✓ Multiple job types (fast, slow, failing)
✓ Status monitoring
✓ Parallel processing with multiple workers
✓ Automatic retry with exponential backoff
✓ Dead Letter Queue for permanent failures

Expected behavior:
- Jobs 1, 2, 3, 5 will complete successfully
- Job 4 (corrupted_file) will fail and move to DLQ after 2 retries
- Workers will process jobs in parallel
- Failed job can be retried from DLQ

Next steps:
1. Start workers: queuectl worker start --count 2
2. Monitor: queuectl status
3. Check results: queuectl list
4. Handle failures: queuectl dlq list
""")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
