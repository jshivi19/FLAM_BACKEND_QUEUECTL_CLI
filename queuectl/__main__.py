#!/usr/bin/env python3
"""
queuectl - A CLI-based background job queue system
"""

import sys
import argparse
import json
from .commands import enqueue, worker, status, list_jobs, dlq, config

def main():
    parser = argparse.ArgumentParser(
        description='queuectl - A CLI-based background job queue system',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Enqueue command
    enqueue_parser = subparsers.add_parser('enqueue', help='Add a new job to the queue')
    enqueue_parser.add_argument('job_json', help='Job definition in JSON format')

    # Worker command
    worker_parser = subparsers.add_parser('worker', help='Manage worker processes')
    worker_subparsers = worker_parser.add_subparsers(dest='worker_command')
    worker_start_parser = worker_subparsers.add_parser('start', help='Start worker processes')
    worker_start_parser.add_argument('--count', type=int, default=1, help='Number of workers (default: 1)')
    worker_stop_parser = worker_subparsers.add_parser('stop', help='Stop worker processes')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show summary of all job states & active workers')

    # List command
    list_parser = subparsers.add_parser('list', help='List jobs by state')
    list_parser.add_argument('--state', help='Filter by state (pending, processing, completed, failed, dead)')

    # DLQ command
    dlq_parser = subparsers.add_parser('dlq', help='Manage Dead Letter Queue')
    dlq_subparsers = dlq_parser.add_subparsers(dest='dlq_command')
    dlq_list_parser = dlq_subparsers.add_parser('list', help='List jobs in DLQ')
    dlq_retry_parser = dlq_subparsers.add_parser('retry', help='Retry a job from DLQ')
    dlq_retry_parser.add_argument('job_id', help='Job ID to retry')

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', help='Config key (max_retries, backoff_base)')
    config_set_parser.add_argument('value', help='Config value')

    args = parser.parse_args()

    try:
        if args.command == 'enqueue':
            try:
                job_data = json.loads(args.job_json)
            except json.JSONDecodeError:
                # Try to handle Windows PowerShell quote issues
                # If it looks like a dict string without quotes, try to fix it
                job_str = args.job_json
                if not job_str.startswith('{'):
                    # Might be split across multiple args, shouldn't happen but handle it
                    print("Error: Invalid JSON format. Use single quotes around the JSON string.", file=sys.stderr)
                    print("Example: queuectl enqueue '{\"id\":\"job1\",\"command\":\"echo test\"}'", file=sys.stderr)
                    sys.exit(1)
                job_data = json.loads(job_str)
            enqueue.handle_enqueue(job_data)
        elif args.command == 'worker':
            if args.worker_command == 'start':
                worker.start_workers(args.count)
            elif args.worker_command == 'stop':
                worker.stop_workers()
            else:
                worker_parser.print_help()
        elif args.command == 'status':
            status.show_status()
        elif args.command == 'list':
            list_jobs.show_list(args.state)
        elif args.command == 'dlq':
            if args.dlq_command == 'list':
                dlq.list_dlq()
            elif args.dlq_command == 'retry':
                dlq.retry_job(args.job_id)
            else:
                dlq_parser.print_help()
        elif args.command == 'config':
            if args.config_command == 'set':
                config.set_config(args.key, args.value)
            else:
                config_parser.print_help()
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
