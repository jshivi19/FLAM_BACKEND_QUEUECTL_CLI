# QueueCTL - Installation and Testing Guide

Complete guide to install, verify, and test QueueCTL.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Terminal/Command Prompt

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd queuectl
```

### 2. Install Dependencies

```bash
pip install -e .
```

This installs queuectl in "editable" mode, making the `queuectl` command available system-wide.

### 3. Verify Installation

```bash
python verify_install.py
```

Expected output:
```
==================================================
QUEUECTL INSTALLATION VERIFICATION
==================================================

Testing: queuectl command available... ✅ PASSED
Testing: enqueue command... ✅ PASSED
Testing: worker command... ✅ PASSED
Testing: status command... ✅ PASSED
Testing: list command... ✅ PASSED
Testing: dlq command... ✅ PASSED
Testing: config command... ✅ PASSED

==================================================
Results: 7 passed, 0 failed
==================================================

✅ All tests passed! QueueCTL is ready to use.
```

## Quick Test

### Test 1: Basic Functionality

```bash
# Enqueue a simple job
queuectl enqueue '{"id":"test1","command":"echo Hello QueueCTL"}'

# Check status
queuectl status

# Start a worker (in a new terminal or background)
queuectl worker start
```

Press Ctrl+C to stop the worker after the job completes.

### Test 2: View Results

```bash
# List all jobs
queuectl list

# List completed jobs
queuectl list --state completed
```

## Comprehensive Testing

### Run Automated Test Suite

```bash
python test_queuectl.py
```

This runs a comprehensive test suite covering:
- Job enqueuing
- Status reporting
- Job listing
- Configuration
- Worker execution
- Dead Letter Queue

Expected output:
```
============================================================
QUEUECTL TEST SUITE
============================================================

=== Test 1: Enqueue Jobs ===
✓ Job enqueued successfully

=== Test 2: Status ===
✓ Status command works

=== Test 3: List Jobs ===
✓ List command works
✓ List with state filter works

=== Test 4: Configuration ===
✓ Configuration works

=== Test 5: Worker Execution ===
✓ Worker processed job successfully

=== Test 6: Dead Letter Queue ===
✓ DLQ command works
✓ Failed job moved to DLQ

=== Cleanup ===
✓ Test data cleaned up

============================================================
ALL TESTS COMPLETED
============================================================
```

### Run Interactive Demo

```bash
python demo.py
```

This sets up a demo environment with sample jobs. Then start workers:

```bash
queuectl worker start
```

### Run Example Workflow

```bash
python example_workflow.py
```

This demonstrates a realistic batch processing scenario.

## Manual Testing Scenarios

### Scenario 1: Successful Job Execution

```bash
# Enqueue job
queuectl enqueue '{"id":"success1","command":"echo Success"}'

# Start worker
queuectl worker start

# Verify completion
queuectl list --state completed
```

### Scenario 2: Failed Job with Retry

```bash
# Enqueue failing job
queuectl enqueue '{"id":"fail1","command":"exit 1","max_retries":2}'

# Start worker (watch it retry)
queuectl worker start

# Check DLQ after retries exhausted
queuectl dlq list
```

### Scenario 3: Multiple Workers

```bash
# Enqueue multiple jobs
queuectl enqueue '{"id":"job1","command":"sleep 2 && echo Job 1"}'
queuectl enqueue '{"id":"job2","command":"sleep 2 && echo Job 2"}'
queuectl enqueue '{"id":"job3","command":"sleep 2 && echo Job 3"}'

# Start 3 workers (processes jobs in parallel)
queuectl worker start --count 3

# Monitor status in another terminal
queuectl status
```

### Scenario 4: Configuration

```bash
# Set max retries
queuectl config set max_retries 5

# Set backoff base
queuectl config set backoff_base 3

# Enqueue job with new config
queuectl enqueue '{"id":"config_test","command":"exit 1"}'

# Worker will retry 5 times with base-3 backoff
queuectl worker start
```

### Scenario 5: DLQ Operations

```bash
# Create a failing job
queuectl enqueue '{"id":"dlq_test","command":"invalid_command","max_retries":1}'

# Process it (will fail and go to DLQ)
queuectl worker start

# List DLQ
queuectl dlq list

# Retry from DLQ
queuectl dlq retry dlq_test

# Process again
queuectl worker start
```

### Scenario 6: Persistence Test

```bash
# Enqueue jobs
queuectl enqueue '{"id":"persist1","command":"echo Test 1"}'
queuectl enqueue '{"id":"persist2","command":"echo Test 2"}'

# Check status
queuectl status

# Close terminal and reopen

# Jobs should still be there
queuectl status
queuectl list
```

## Troubleshooting

### Issue: "Command not found: queuectl"

**Solution:**
```bash
# Try running directly
python -m queuectl --help

# Or reinstall
pip install -e .

# Check Python scripts directory is in PATH
pip show queuectl
```

### Issue: Workers not processing jobs

**Checklist:**
1. Are workers running? `queuectl status`
2. Are jobs pending? `queuectl list --state pending`
3. Check worker output for errors
4. Verify job commands are valid

### Issue: Jobs stuck in "processing"

**Cause:** Worker crashed while processing

**Solution:**
```bash
# Manually edit .queuectl/jobs.json
# Change job state from "processing" to "pending"
# Or delete and re-enqueue the job
```

### Issue: Permission errors

**Solution:**
```bash
# Check .queuectl directory permissions
ls -la .queuectl

# If needed, fix permissions
chmod -R u+rw .queuectl
```

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Reinstall package
pip install -e .
```

## Platform-Specific Notes

### Windows

- File locking uses `msvcrt`
- SIGTERM not available (only SIGINT)
- Use Ctrl+C to stop workers
- May need to manually kill worker processes

### Linux/macOS

- File locking uses `fcntl`
- Full signal support (SIGINT, SIGTERM)
- Graceful shutdown works perfectly
- Can use `kill` command for workers

## Performance Testing

### Test Throughput

```bash
# Enqueue 100 jobs
for i in {1..100}; do
  queuectl enqueue "{\"id\":\"perf$i\",\"command\":\"echo Job $i\"}"
done

# Process with multiple workers
queuectl worker start --count 5

# Monitor completion
watch -n 1 queuectl status
```

### Test Concurrency

```bash
# Enqueue long-running jobs
for i in {1..10}; do
  queuectl enqueue "{\"id\":\"long$i\",\"command\":\"sleep 5 && echo Done $i\"}"
done

# Start multiple workers
queuectl worker start --count 3

# Verify parallel execution
queuectl status
```

## Cleanup

### Remove Test Data

```bash
# Remove job data
rm -rf .queuectl

# Remove config
rm -rf ~/.queuectl
```

### Uninstall

```bash
pip uninstall queuectl
```

## Next Steps

After successful installation and testing:

1. **Read Documentation**
   - [README.md](README.md) - Complete documentation
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide
   - [DESIGN.md](DESIGN.md) - Architecture details

2. **Build Your Workflows**
   - Create job processing pipelines
   - Integrate with existing systems
   - Customize retry behavior

3. **Monitor and Maintain**
   - Regular status checks
   - DLQ monitoring
   - Log analysis

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review README.md for detailed documentation
3. Examine .queuectl/jobs.json for job state
4. Run verify_install.py to check installation
5. Check Python and pip versions

## Success Criteria

✅ `verify_install.py` passes all tests  
✅ Can enqueue jobs successfully  
✅ Workers process jobs correctly  
✅ Failed jobs move to DLQ  
✅ Configuration persists  
✅ Jobs survive restart  
✅ Multiple workers work in parallel  

If all criteria are met, QueueCTL is ready for production use!

---

**Happy queuing! 🚀**
