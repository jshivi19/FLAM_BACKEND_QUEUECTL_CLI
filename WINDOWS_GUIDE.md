# QueueCTL - Windows PowerShell Guide

Special guide for running QueueCTL on Windows PowerShell.

## Installation

```powershell
cd queuectl
pip install -e .
```

## The Quote Problem

PowerShell handles quotes differently than bash. Here are the solutions:

## Solution 1: Use Helper Scripts (Easiest)

### Enqueue Jobs

```powershell
python enqueue_job.py job1 "echo Hello World"
python enqueue_job.py job2 "echo Task 2"
python enqueue_job.py job3 "timeout 2" 5
```

### Run Quick Demo

```powershell
python quick_demo.py
```

Then start workers:
```powershell
queuectl worker start
```

## Solution 2: Use Python Module Syntax

```powershell
python -m queuectl enqueue '{\"id\":\"job1\",\"command\":\"echo Hello\"}'
python -m queuectl status
python -m queuectl list
python -m queuectl worker start
```

## Solution 3: Create a Batch File

Create `add_jobs.bat`:
```batch
@echo off
queuectl enqueue "{\"id\":\"job1\",\"command\":\"echo Hello World\"}"
queuectl enqueue "{\"id\":\"job2\",\"command\":\"echo Task 2\"}"
queuectl enqueue "{\"id\":\"job3\",\"command\":\"timeout 2\"}"
```

Run it:
```powershell
.\add_jobs.bat
```

## Complete Working Example

### Step 1: Setup and Add Jobs

```powershell
# Run the quick demo
python quick_demo.py
```

### Step 2: Start Workers (New Terminal)

```powershell
cd queuectl
queuectl worker start --count 2
```

### Step 3: Monitor (Another Terminal)

```powershell
cd queuectl
queuectl status
queuectl list
```

## Using the Helper Script

The `enqueue_job.py` helper makes it easy:

```powershell
# Basic job
python enqueue_job.py myJob "echo Hello"

# Job with custom retries
python enqueue_job.py myJob "echo Hello" 5

# Multiple jobs
python enqueue_job.py job1 "echo Task 1"
python enqueue_job.py job2 "echo Task 2"
python enqueue_job.py job3 "timeout 3"
```

## All Commands That Work

```powershell
# These work fine (no JSON needed)
queuectl status
queuectl list
queuectl list --state pending
queuectl list --state completed
queuectl dlq list
queuectl worker start
queuectl worker start --count 3
queuectl config set max_retries 5
queuectl config set backoff_base 2

# For enqueuing, use the helper:
python enqueue_job.py <id> <command> [retries]
```

## Quick Test

```powershell
# 1. Add jobs using helper
python enqueue_job.py test1 "echo Hello"
python enqueue_job.py test2 "echo World"

# 2. Check status
queuectl status

# 3. Start worker
queuectl worker start
```

## Troubleshooting

### "Expecting value: line 1 column 1"

This means the JSON wasn't parsed correctly. Use the helper script instead:

```powershell
# Instead of:
queuectl enqueue '{"id":"job1","command":"echo test"}'

# Use:
python enqueue_job.py job1 "echo test"
```

### Worker Not Processing

```powershell
# Check if jobs are there
queuectl list --state pending

# Check if worker is running
queuectl status

# Try starting worker
queuectl worker start
```

## Complete Workflow Example

```powershell
# Terminal 1: Setup and monitor
cd queuectl

# Add jobs
python enqueue_job.py process1 "echo Processing file 1"
python enqueue_job.py process2 "echo Processing file 2"
python enqueue_job.py process3 "echo Processing file 3"

# Check status
queuectl status

# Monitor
queuectl list
```

```powershell
# Terminal 2: Run workers
cd queuectl
queuectl worker start --count 2
```

Press Ctrl+C to stop workers.

## Summary

**For Windows PowerShell, use:**
- ✅ `python enqueue_job.py <id> <command>` - To add jobs
- ✅ `python quick_demo.py` - For quick demo
- ✅ `queuectl status` - Check status
- ✅ `queuectl list` - List jobs
- ✅ `queuectl worker start` - Start workers

**Avoid:**
- ❌ Direct JSON in PowerShell (quote issues)

Happy queuing on Windows! 🚀
