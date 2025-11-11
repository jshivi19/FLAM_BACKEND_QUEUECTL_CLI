import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from .job_queue import JobQueue
from .job import JobState
from .config import get_config

class WorkerManager:
    def __init__(self):
        self.queue = JobQueue()
        self.config = get_config()
        self.running = True
        self.pid_file = self.config.get_data_dir() / "workers.pid"
    
    def calculate_backoff(self, attempts):
        """Calculate exponential backoff delay"""
        base = self.config.get("backoff_base", 2)
        return base ** attempts
    
    def execute_job(self, job):
        """Execute a job command"""
        try:
            result = subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Job timed out"
        except Exception as e:
            return False, "", str(e)
    
    def process_job(self, job):
        """Process a single job with retry logic"""
        job.increment_attempt()
        
        success, stdout, stderr = self.execute_job(job)
        
        if success:
            job.mark_completed()
            print(f"✓ Job {job.id} completed successfully")
        else:
            if job.should_retry():
                job.mark_failed()
                delay = self.calculate_backoff(job.attempts)
                print(f"✗ Job {job.id} failed (attempt {job.attempts}/{job.max_retries}). Retrying in {delay}s...")
                time.sleep(delay)
                job.state = JobState.PENDING
            else:
                job.mark_dead()
                print(f"☠ Job {job.id} moved to DLQ after {job.attempts} attempts")
        
        self.queue.update_job(job)
    
    def run_worker(self):
        """Main worker loop"""
        print(f"Worker started (PID: {os.getpid()})")
        
        def signal_handler(sig, frame):
            print("\nGracefully shutting down worker...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        
        while self.running:
            job = self.queue.get_next_job()
            if job:
                self.process_job(job)
            else:
                time.sleep(1)
        
        print("Worker stopped")
    
    def start_workers(self, count):
        """Start multiple worker processes"""
        import multiprocessing
        
        pids = []
        for i in range(count):
            p = multiprocessing.Process(target=self.run_worker)
            p.start()
            pids.append(p.pid)
        
        # Save PIDs
        with open(self.pid_file, 'w') as f:
            f.write('\n'.join(map(str, pids)))
        
        print(f"Started {count} worker(s)")
        
        # Wait for all workers
        for p in multiprocessing.active_children():
            p.join()
    
    def stop_workers(self):
        """Stop all running workers"""
        if not self.pid_file.exists():
            print("No workers running")
            return
        
        with open(self.pid_file, 'r') as f:
            pids = [int(line.strip()) for line in f if line.strip()]
        
        try:
            import psutil
            stopped = 0
            for pid in pids:
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                    p.wait(timeout=5)
                    stopped += 1
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
            
            self.pid_file.unlink()
            print(f"Stopped {stopped} worker(s)")
        except ImportError:
            print("psutil not installed. Please stop workers manually or install psutil.")
            print(f"Worker PIDs: {', '.join(map(str, pids))}")
    
    def get_active_workers(self):
        """Get list of active worker PIDs"""
        if not self.pid_file.exists():
            return []
        
        with open(self.pid_file, 'r') as f:
            pids = [int(line.strip()) for line in f if line.strip()]
        
        try:
            import psutil
            active = []
            for pid in pids:
                try:
                    p = psutil.Process(pid)
                    if p.is_running():
                        active.append(pid)
                except psutil.NoSuchProcess:
                    pass
            return active
        except ImportError:
            # If psutil not available, return all PIDs
            return pids
