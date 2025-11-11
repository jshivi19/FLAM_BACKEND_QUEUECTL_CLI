# Getting Started with QueueCTL

Welcome! This guide will get you up and running with QueueCTL in under 10 minutes.

## What You'll Learn

1. How to install QueueCTL
2. How to enqueue your first job
3. How to start workers
4. How to monitor job execution
5. How to handle failures

## Step-by-Step Guide

### Step 1: Install QueueCTL (2 minutes)

```bash
cd queuectl
pip install -e .
```

Verify installation:
```bash
python verify_install.py
```

You should see all tests pass ✅

### Step 2: Your First Job (1 minute)

Let's enqueue a simple job:

```bash
queuectl enqueue '{"id":"hello","command":"echo Hello, QueueCTL!"}'
```

You should see:
```
✓ Job enqueued: hello
  Command: echo Hello, QueueCTL!
  Max retries: 3
```

Check the status:
```bash
queuectl status
```

### Step 3: Start a Worker (1 minute)

Open a new terminal and start a worker:

```bash
queuectl worker start
```

You'll see:
```
Worker started (PID: 12345)
✓ Job hello completed successfully
```

The worker will keep running, waiting for more jobs. Press Ctrl+C to stop it.

### Step 4: Enqueue Multiple Jobs (2 minutes)

Let's enqueue several jobs:

```bash
queuectl enqueue '{"id":"job1","command":"echo Task 1"}'
queuectl enqueue '{"id":"job2","command":"echo Task 2"}'
queuectl enqueue '{"id":"job3","command":"sleep 2 && echo Task 3"}'
```

Start multiple workers to process them in parallel:

```bash
queuectl worker start --count 3
```

### Step 5: Monitor Progress (1 minute)

In another terminal, check the status:

```bash
queuectl status
```

List all jobs:
```bash
queuectl list
```

List only completed jobs:
```bash
queuectl list --state completed
```

### Step 6: Handle Failures (3 minutes)

Let's see how QueueCTL handles failures:

```bash
queuectl enqueue '{"id":"fail_test","command":"exit 1","max_retries":2}'
```

Start a worker:
```bash
queuectl worker start
```

Watch the output - you'll see:
```
✗ Job fail_test failed (attempt 1/2). Retrying in 2s...
✗ Job fail_test failed (attempt 2/2). Retrying in 4s...
☠ Job fail_test moved to DLQ after 2 attempts
```

Check the Dead Letter Queue:
```bash
queuectl dlq list
```

Retry the failed job:
```bash
queuectl dlq retry fail_test
```

## Common Commands Cheat Sheet

```bash
# Enqueue a job
queuectl enqueue '{"id":"my_job","command":"echo Hello"}'

# Start workers
queuectl worker start              # Single worker
queuectl worker start --count 3    # Multiple workers

# Monitor
queuectl status                    # Overall status
queuectl list                      # All jobs
queuectl list --state pending      # Filter by state

# Dead Letter Queue
queuectl dlq list                  # View failed jobs
queuectl dlq retry <job_id>        # Retry a job

# Configuration
queuectl config set max_retries 5
queuectl config set backoff_base 2
```

## Real-World Example

Let's simulate a batch file processing workflow:

```bash
# Configure
queuectl config set max_retries 3

# Enqueue batch jobs
queuectl enqueue '{"id":"process1","command":"echo Processing file1.txt"}'
queuectl enqueue '{"id":"process2","command":"echo Processing file2.txt"}'
queuectl enqueue '{"id":"process3","command":"echo Processing file3.txt"}'

# Process with 2 workers
queuectl worker start --count 2

# Monitor in another terminal
watch -n 1 queuectl status
```

## Understanding Job States

Jobs flow through these states:

```
PENDING → PROCESSING → COMPLETED ✓
    ↓          ↓
    ↓      FAILED → (retry) → PENDING
    ↓          ↓
    └──────→ DEAD (DLQ) ☠
```

- **PENDING**: Waiting to be processed
- **PROCESSING**: Currently being executed
- **COMPLETED**: Successfully finished
- **FAILED**: Failed but will retry
- **DEAD**: Permanently failed (in DLQ)

## Understanding Exponential Backoff

When a job fails, QueueCTL waits before retrying:

- Attempt 1 fails → wait 2 seconds (2^1)
- Attempt 2 fails → wait 4 seconds (2^2)
- Attempt 3 fails → wait 8 seconds (2^3)
- Max retries reached → move to DLQ

This prevents overwhelming failing services.

## Tips for Success

1. **Run workers in a separate terminal** - Makes monitoring easier
2. **Use meaningful job IDs** - Helps with debugging
3. **Check status regularly** - `queuectl status` is your friend
4. **Monitor the DLQ** - Don't let failed jobs pile up
5. **Configure retries appropriately** - More retries for transient failures
6. **Test with simple commands first** - Like `echo` before complex scripts

## Troubleshooting

### Workers not processing jobs?

```bash
# Check if workers are running
queuectl status

# Check if jobs are pending
queuectl list --state pending

# Try starting a worker with verbose output
queuectl worker start
```

### Jobs stuck in processing?

This happens if a worker crashes. The job remains in "processing" state.

**Solution:** Edit `.queuectl/jobs.json` and change the state to "pending", or re-enqueue the job.

### Command not found?

```bash
# Try running directly
python -m queuectl --help

# Or check installation
pip show queuectl
```

## Next Steps

Now that you're familiar with the basics:

1. **Run the demo**: `python demo.py`
2. **Try the example workflow**: `python example_workflow.py`
3. **Read the full documentation**: [README.md](README.md)
4. **Understand the architecture**: [DESIGN.md](DESIGN.md)
5. **Build your own workflows!**

## Quick Reference

### Job JSON Format

```json
{
  "id": "unique-job-id",
  "command": "shell command to execute",
  "max_retries": 3
}
```

### Configuration Options

- `max_retries`: Number of retry attempts (default: 3)
- `backoff_base`: Exponential backoff base (default: 2)
- `data_dir`: Data storage location (default: .queuectl)

### Data Files

- `.queuectl/jobs.json` - All job data
- `.queuectl/workers.pid` - Active worker PIDs
- `~/.queuectl/config.json` - User configuration

## Help and Documentation

- `queuectl --help` - Main help
- `queuectl <command> --help` - Command-specific help
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick reference
- [DESIGN.md](DESIGN.md) - Architecture details
- [INSTALL_AND_TEST.md](INSTALL_AND_TEST.md) - Testing guide

## Success!

You're now ready to use QueueCTL for your background job processing needs!

Key takeaways:
- ✅ Jobs are persistent (survive restarts)
- ✅ Workers can run in parallel
- ✅ Failed jobs retry automatically
- ✅ Permanently failed jobs go to DLQ
- ✅ Everything is configurable

Happy queuing! 🚀

---

**Need help?** Check the troubleshooting section in [README.md](README.md) or review the examples in [QUICKSTART.md](QUICKSTART.md).
