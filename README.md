# QueueCTL - Background Job Queue System

A production-grade CLI-based background job queue system with worker processes, retry logic with exponential backoff, and Dead Letter Queue (DLQ) support.

## Features

✅ Job enqueuing and management  
✅ Multiple concurrent worker processes  
✅ Automatic retry with exponential backoff  
✅ Dead Letter Queue for permanently failed jobs  
✅ Persistent storage (survives restarts)  
✅ File-based locking for concurrency safety  
✅ Configurable retry and backoff settings  
✅ Clean CLI interface  

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip

### Installation

```bash
cd queuectl
pip install -e .
```

This installs `queuectl` as a command-line tool.

### Verify Installation

```bash
python verify_install.py
```

This will test all commands and confirm everything is working.

### Platform Notes

**Windows:**
- Uses `msvcrt` for file locking
- SIGTERM not available (uses SIGINT only)
- Worker stop may require manual termination

**Linux/Mac:**
- Uses `fcntl` for file locking
- Full signal support
- Graceful worker shutdown

## Usage Examples

### 1. Enqueue Jobs

```bash
# Simple job
queuectl enqueue '{"id":"job1","command":"echo Hello World"}'

# Job with custom retry limit
queuectl enqueue '{"id":"job2","command":"sleep 2","max_retries":5}'

# Job that will fail
queuectl enqueue '{"id":"job3","command":"exit 1"}'
```

### 2. Start Workers

```bash
# Start a single worker
queuectl worker start

# Start multiple workers
queuectl worker start --count 3
```

Workers run in the foreground. Press Ctrl+C to stop gracefully.

### 3. Check Status

```bash
queuectl status
```

Output:
```
==================================================
QUEUECTL STATUS
==================================================

Active Workers: 3
  PIDs: 12345, 12346, 12347

Job Statistics:
  Pending:    5
  Processing: 2
  Completed:  10
  Failed:     1
  Dead (DLQ): 2
  Total:      20
==================================================
```

### 4. List Jobs

```bash
# List all jobs
queuectl list

# List by state
queuectl list --state pending
queuectl list --state completed
queuectl list --state dead
```

### 5. Manage Dead Letter Queue

```bash
# View DLQ
queuectl dlq list

# Retry a failed job
queuectl dlq retry job1
```

### 6. Configuration

```bash
# Set max retries (default: 3)
queuectl config set max_retries 5

# Set backoff base (default: 2)
queuectl config set backoff_base 3
```

Backoff formula: `delay = base ^ attempts` seconds

## Architecture Overview

### Components

1. **Job Queue** - Manages job lifecycle and state transitions
2. **Job Storage** - Persistent file-based storage with locking
3. **Worker Manager** - Spawns and manages worker processes
4. **Workers** - Execute jobs with retry logic
5. **CLI** - Command-line interface for all operations

### Job Lifecycle

```
PENDING → PROCESSING → COMPLETED
    ↓          ↓
    ↓      FAILED (retry)
    ↓          ↓
    └──────→ DEAD (DLQ)
```

### Data Persistence

- Jobs stored in `.queuectl/jobs.json`
- Configuration in `~/.queuectl/config.json`
- File locking prevents race conditions
- Worker PIDs tracked in `.queuectl/workers.pid`

### Concurrency Safety

- File-based locking using `fcntl` (POSIX systems)
- Atomic read-modify-write operations
- Workers acquire lock before job state changes
- Prevents duplicate job processing

### Retry Logic

1. Job fails → increment attempt counter
2. Check if `attempts < max_retries`
3. If yes: calculate backoff delay and retry
4. If no: move to DLQ (DEAD state)

**Exponential Backoff:**
- Attempt 1: 2^1 = 2 seconds
- Attempt 2: 2^2 = 4 seconds
- Attempt 3: 2^3 = 8 seconds

## Testing Instructions

### Manual Testing

Run the included test script:

```bash
cd queuectl
python test_queuectl.py
```

### Test Scenarios

1. **Basic Job Completion**
   ```bash
   queuectl enqueue '{"id":"test1","command":"echo success"}'
   queuectl worker start
   # Check: job should complete
   ```

2. **Failed Job with Retry**
   ```bash
   queuectl enqueue '{"id":"test2","command":"exit 1","max_retries":2}'
   queuectl worker start
   # Check: job retries 2 times then moves to DLQ
   ```

3. **Multiple Workers**
   ```bash
   # Enqueue multiple jobs
   for i in {1..5}; do
     queuectl enqueue "{\"id\":\"job$i\",\"command\":\"sleep 2\"}"
   done
   
   # Start 3 workers
   queuectl worker start --count 3
   # Check: jobs processed in parallel
   ```

4. **Persistence Test**
   ```bash
   queuectl enqueue '{"id":"persist1","command":"echo test"}'
   queuectl status  # Note job count
   # Restart terminal/system
   queuectl status  # Job still there
   ```

5. **DLQ Operations**
   ```bash
   queuectl enqueue '{"id":"dlq1","command":"invalid_command"}'
   queuectl worker start
   # Wait for job to fail and move to DLQ
   queuectl dlq list
   queuectl dlq retry dlq1
   ```

## Assumptions & Trade-offs

### Assumptions
- Jobs are shell commands (not arbitrary Python functions)
- Single-machine deployment (not distributed)
- File system supports POSIX file locking
- Jobs complete within 5 minutes (timeout)

### Trade-offs

**File-based Storage vs Database:**
- ✅ Simple, no external dependencies
- ✅ Easy to inspect and debug
- ❌ Not suitable for high-throughput scenarios
- ❌ Limited query capabilities

**Process-based Workers vs Threads:**
- ✅ True parallelism (no GIL)
- ✅ Isolation (crash doesn't affect others)
- ❌ Higher memory overhead
- ❌ More complex IPC

**Exponential Backoff:**
- ✅ Reduces load on failing services
- ✅ Industry standard approach
- ❌ Can lead to long delays

## Project Structure

```
queuectl/
├── queuectl/                # Main package
│   ├── commands/            # CLI command handlers
│   ├── storage/             # Persistence layer
│   ├── __main__.py          # CLI entry point
│   ├── job.py               # Job model
│   ├── job_queue.py         # Queue management
│   ├── worker_manager.py    # Worker orchestration
│   └── config.py            # Configuration
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── README.md                # This file
├── QUICKSTART.md            # Quick reference
├── DESIGN.md                # Architecture details
├── WINDOWS_GUIDE.md         # Windows-specific help
├── enqueue_job.py           # Helper script for Windows
├── quick_demo.py            # Quick demo script
├── test_queuectl.py         # Test suite
└── verify_install.py        # Installation verification
```

## Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference and common commands
- **[DESIGN.md](DESIGN.md)** - Detailed architecture and design decisions
- **[WINDOWS_GUIDE.md](WINDOWS_GUIDE.md)** - Windows PowerShell specific instructions

## Demo Video

https://drive.google.com/file/d/1H1sdTNqOjfNrN-4gS_CtOlQaJ5bGSYvy/view?usp=sharing

## Future Enhancements

- Job priority queues
- Scheduled/delayed jobs
- Job output logging
- Web dashboard
- Distributed workers
- Job dependencies
- Metrics and monitoring
## Integration with Kafka
QueueCTL can be extended with **Apache Kafka** to enable distributed and fault-tolerant job processing. Jobs are published to partitioned Kafka topics for parallel execution by worker consumers. Failed jobs are retried with exponential backoff and moved to a **Dead Letter Queue (DLQ)** after exceeding retry limits. This architecture provides scalability, persistence, and fault isolation for reliable background job management.


## License

MIT

## Author

Shivi Jain
