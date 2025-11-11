# QueueCTL Quick Start Guide

Get up and running with QueueCTL in 5 minutes!

## Installation

```bash
cd queuectl
pip install -e .
```

## Basic Usage

### 1. Enqueue a Job

```bash
queuectl enqueue '{"id":"hello","command":"echo Hello World"}'
```

### 2. Start a Worker

```bash
queuectl worker start
```

The worker will process jobs and display output. Press Ctrl+C to stop.

### 3. Check Status

Open a new terminal and run:

```bash
queuectl status
```

## Common Workflows

### Run Multiple Workers

```bash
queuectl worker start --count 3
```

### Enqueue Multiple Jobs

```bash
queuectl enqueue '{"id":"job1","command":"echo Task 1"}'
queuectl enqueue '{"id":"job2","command":"sleep 2 && echo Task 2"}'
queuectl enqueue '{"id":"job3","command":"echo Task 3"}'
```

### View All Jobs

```bash
queuectl list
```

### View Jobs by State

```bash
queuectl list --state pending
queuectl list --state completed
queuectl list --state failed
```

### Configure Retries

```bash
queuectl config set max_retries 5
queuectl config set backoff_base 2
```

### Test Failure Handling

```bash
# Enqueue a job that will fail
queuectl enqueue '{"id":"fail_test","command":"exit 1","max_retries":2}'

# Start worker to process it
queuectl worker start

# After it fails, check DLQ
queuectl dlq list

# Retry the failed job
queuectl dlq retry fail_test
```

## Demo Script

Run the included demo:

```bash
python demo.py
```

Then start workers:

```bash
queuectl worker start
```

## Tips

1. **Workers run in foreground** - Use Ctrl+C to stop gracefully
2. **Jobs persist** - Restart workers anytime, jobs remain
3. **Multiple terminals** - Run workers in one, commands in another
4. **Check status often** - Use `queuectl status` to monitor
5. **DLQ is your friend** - Failed jobs go there, you can retry them

## Troubleshooting

### "Command not found: queuectl"

Make sure you installed with `pip install -e .` and your Python scripts directory is in PATH.

### Workers not processing jobs

1. Check if workers are running: `queuectl status`
2. Check if jobs are pending: `queuectl list --state pending`
3. Check for errors in worker output

### Jobs stuck in "processing"

This can happen if a worker crashes. The job will remain in processing state. You can manually fix by editing `.queuectl/jobs.json` and changing the state back to "pending".

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DESIGN.md](DESIGN.md) for architecture details
- Run tests with `python test_queuectl.py`
- Build your own job workflows!

## Example: Processing Files

```bash
# Enqueue file processing jobs
queuectl enqueue '{"id":"process1","command":"python process.py file1.txt"}'
queuectl enqueue '{"id":"process2","command":"python process.py file2.txt"}'
queuectl enqueue '{"id":"process3","command":"python process.py file3.txt"}'

# Process with 2 workers
queuectl worker start --count 2
```

## Example: Scheduled Tasks

```bash
# Morning backup
queuectl enqueue '{"id":"backup1","command":"tar -czf backup.tar.gz data/"}'

# Data processing
queuectl enqueue '{"id":"etl1","command":"python etl_pipeline.py"}'

# Cleanup
queuectl enqueue '{"id":"cleanup1","command":"find /tmp -mtime +7 -delete"}'
```

Happy queuing! 🚀
