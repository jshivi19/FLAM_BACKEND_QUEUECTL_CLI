# QueueCTL - Architecture & Design

## Overview

QueueCTL is a production-grade background job queue system designed for single-machine deployments. It provides reliable job execution with automatic retries, exponential backoff, and dead letter queue support.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
│  (enqueue, worker, status, list, dlq, config)           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  Core Components                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Job Queue   │  │Worker Manager│  │   Config     │ │
│  │              │  │              │  │              │ │
│  │ - enqueue    │  │ - spawn      │  │ - settings   │ │
│  │ - get_next   │  │ - execute    │  │ - persist    │ │
│  │ - update     │  │ - retry      │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘ │
│         │                  │                            │
└─────────┼──────────────────┼────────────────────────────┘
          │                  │
┌─────────┴──────────────────┴────────────────────────────┐
│              Persistence Layer                           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Job Storage (File-based)                │  │
│  │                                                   │  │
│  │  - jobs.json (job data)                          │  │
│  │  - File locking (concurrency safety)             │  │
│  │  - Atomic operations                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Job Model

**Fields:**
- `id`: Unique identifier
- `command`: Shell command to execute
- `state`: Current state (pending, processing, completed, failed, dead)
- `attempts`: Number of execution attempts
- `max_retries`: Maximum retry attempts
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**State Machine:**
```
PENDING ──┐
          ├──> PROCESSING ──> COMPLETED
          │         │
          │         ├──> FAILED ──> PENDING (retry)
          │         │
          └─────────┴──> DEAD (DLQ)
```

### 2. Job Queue

**Responsibilities:**
- Accept new jobs
- Provide next available job to workers
- Update job state
- Query jobs by state
- Generate statistics

**Key Methods:**
- `enqueue(job_data)`: Add job to queue
- `get_next_job()`: Atomically get and mark job as processing
- `update_job(job)`: Persist job state changes
- `get_jobs_by_state(state)`: Filter jobs
- `get_stats()`: Aggregate statistics

### 3. Job Storage

**Implementation:** File-based JSON storage

**Features:**
- Persistent across restarts
- File locking for concurrency safety
- Atomic read-modify-write operations

**Files:**
- `.queuectl/jobs.json`: All job data
- `.queuectl/workers.pid`: Active worker PIDs
- `~/.queuectl/config.json`: User configuration

**Locking Strategy:**
- Platform-specific: `fcntl` (POSIX) or `msvcrt` (Windows)
- Exclusive locks during read-modify-write
- Prevents race conditions between workers

### 4. Worker Manager

**Responsibilities:**
- Spawn worker processes
- Execute jobs
- Implement retry logic
- Handle graceful shutdown

**Worker Lifecycle:**
1. Start worker process
2. Poll for pending jobs
3. Execute job command
4. Handle success/failure
5. Apply retry logic
6. Update job state
7. Repeat or shutdown

**Retry Logic:**
```python
if job fails:
    attempts += 1
    if attempts < max_retries:
        delay = backoff_base ^ attempts
        sleep(delay)
        state = PENDING  # retry
    else:
        state = DEAD  # move to DLQ
```

**Exponential Backoff:**
- Formula: `delay = base ^ attempts`
- Default base: 2
- Example: 2s, 4s, 8s, 16s...
- Prevents overwhelming failing services

### 5. Configuration

**Settings:**
- `max_retries`: Default retry count (default: 3)
- `backoff_base`: Exponential backoff base (default: 2)
- `data_dir`: Data storage location (default: .queuectl)

**Storage:** `~/.queuectl/config.json`

## Concurrency Model

### Multi-Process Architecture

**Why Processes over Threads?**
- True parallelism (no Python GIL)
- Process isolation (crash doesn't affect others)
- Simpler reasoning about state

**Synchronization:**
- File-based locking
- Atomic state transitions
- No shared memory

### Race Condition Prevention

**Scenario:** Two workers try to process same job

**Solution:**
1. Worker A reads jobs.json (with lock)
2. Worker A marks job as PROCESSING
3. Worker A writes jobs.json (releases lock)
4. Worker B reads jobs.json (with lock)
5. Worker B sees job is PROCESSING, skips it

**Critical Section:**
```python
with file_lock:
    jobs = read_jobs()
    job = find_pending_job(jobs)
    job.state = PROCESSING
    write_jobs(jobs)
```

## Data Flow

### Enqueue Flow
```
User → CLI → JobQueue.enqueue() → JobStorage.add_job() → jobs.json
```

### Worker Flow
```
Worker Loop:
  1. JobStorage.get_next_pending_job() [LOCK]
  2. Mark as PROCESSING [LOCK]
  3. Execute command
  4. Update state (COMPLETED/FAILED/DEAD) [LOCK]
  5. If FAILED and retries left: sleep + mark PENDING [LOCK]
```

### DLQ Flow
```
Failed Job (max retries) → Mark as DEAD → DLQ
User → dlq retry → Mark as PENDING → Back to queue
```

## Design Decisions

### 1. File-based Storage

**Pros:**
- No external dependencies
- Easy to inspect and debug
- Simple backup/restore
- Portable

**Cons:**
- Not suitable for high throughput
- Limited query capabilities
- File I/O overhead

**Alternatives Considered:**
- SQLite: More complex, overkill for requirements
- Redis: External dependency, network overhead
- In-memory: Not persistent

### 2. Shell Command Execution

**Pros:**
- Maximum flexibility
- Language-agnostic
- Leverage existing tools

**Cons:**
- Security concerns (command injection)
- Limited error information
- Platform-specific behavior

**Mitigation:**
- Use `subprocess.run()` with `shell=True` carefully
- Timeout protection (5 minutes)
- Capture stdout/stderr

### 3. Exponential Backoff

**Rationale:**
- Industry standard for retries
- Reduces load on failing services
- Gives transient issues time to resolve

**Configuration:**
- Adjustable base (default: 2)
- Adjustable max retries (default: 3)

### 4. Process-based Workers

**Rationale:**
- True parallelism (no GIL)
- Isolation (one crash doesn't kill all)
- Simpler than distributed system

**Trade-offs:**
- Higher memory usage
- More complex IPC
- Limited to single machine

## Error Handling

### Job Execution Errors

1. **Command not found**: Retry (may be transient)
2. **Non-zero exit code**: Retry with backoff
3. **Timeout**: Fail and retry
4. **Exception**: Fail and retry

### System Errors

1. **File lock timeout**: Retry operation
2. **Disk full**: Log error, continue
3. **Permission denied**: Log error, skip job

### Graceful Degradation

- If locking fails: Best-effort (may have races)
- If psutil unavailable: Manual worker management
- If config missing: Use defaults

## Performance Characteristics

### Throughput

- **Single worker**: ~1-10 jobs/second (depends on job duration)
- **Multiple workers**: Linear scaling up to I/O limits
- **Bottleneck**: File I/O for state updates

### Latency

- **Enqueue**: <10ms (single file write)
- **Job pickup**: <100ms (polling interval: 1s)
- **State update**: <10ms (single file write)

### Scalability Limits

- **Jobs**: ~10,000 (JSON parsing overhead)
- **Workers**: ~10 (file lock contention)
- **Throughput**: ~100 jobs/second (file I/O limit)

**For higher scale:**
- Use database (SQLite, PostgreSQL)
- Implement job sharding
- Use message queue (RabbitMQ, Redis)

## Testing Strategy

### Unit Tests
- Job state transitions
- Retry logic
- Backoff calculation
- Configuration management

### Integration Tests
- End-to-end job execution
- Multi-worker concurrency
- Persistence across restarts
- DLQ operations

### Manual Tests
- Graceful shutdown
- Invalid commands
- System resource limits
- Platform compatibility

## Future Enhancements

### Priority Queue
- Add `priority` field to jobs
- Process high-priority jobs first
- Implement priority-based scheduling

### Scheduled Jobs
- Add `run_at` timestamp
- Skip jobs until scheduled time
- Support cron-like expressions

### Job Dependencies
- Add `depends_on` field
- Wait for dependencies to complete
- Build DAG execution

### Distributed Workers
- Network-based job distribution
- Centralized job storage
- Worker registration/heartbeat

### Monitoring
- Job execution metrics
- Worker health checks
- Performance dashboards
- Alerting on failures

### Job Output
- Capture stdout/stderr
- Store in separate files
- Provide log viewing commands

## Security Considerations

### Command Injection
- **Risk**: Malicious commands in job data
- **Mitigation**: Validate/sanitize commands, run with limited permissions

### File Access
- **Risk**: Unauthorized access to job data
- **Mitigation**: File permissions, user isolation

### Resource Exhaustion
- **Risk**: Jobs consuming excessive resources
- **Mitigation**: Timeouts, resource limits (ulimit)

## Conclusion

QueueCTL provides a solid foundation for background job processing with:
- Reliable execution
- Automatic retries
- Persistent storage
- Concurrent workers
- Simple operation

It's suitable for small to medium workloads on single machines. For larger scale or distributed deployments, consider migrating to a dedicated message queue system.
