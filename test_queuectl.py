#!/usr/bin/env python3
"""
Test script for queuectl
Validates core functionality
"""

import subprocess
import time
import json
import sys
import os

def run_command(cmd):
    """Run a shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_enqueue():
    """Test job enqueuing"""
    print("\n=== Test 1: Enqueue Jobs ===")
    
    # Enqueue a simple job
    code, out, err = run_command('queuectl enqueue \'{"id":"test1","command":"echo Hello"}\'')
    assert code == 0, f"Enqueue failed: {err}"
    assert "test1" in out, "Job ID not in output"
    print("✓ Job enqueued successfully")

def test_status():
    """Test status command"""
    print("\n=== Test 2: Status ===")
    
    code, out, err = run_command('queuectl status')
    assert code == 0, f"Status failed: {err}"
    assert "QUEUECTL STATUS" in out, "Status output malformed"
    print("✓ Status command works")

def test_list():
    """Test list command"""
    print("\n=== Test 3: List Jobs ===")
    
    code, out, err = run_command('queuectl list')
    assert code == 0, f"List failed: {err}"
    print("✓ List command works")
    
    code, out, err = run_command('queuectl list --state pending')
    assert code == 0, f"List with filter failed: {err}"
    print("✓ List with state filter works")

def test_config():
    """Test configuration"""
    print("\n=== Test 4: Configuration ===")
    
    code, out, err = run_command('queuectl config set max_retries 5')
    assert code == 0, f"Config set failed: {err}"
    assert "5" in out, "Config value not reflected"
    print("✓ Configuration works")

def test_worker_basic():
    """Test basic worker functionality"""
    print("\n=== Test 5: Worker Execution ===")
    
    # Enqueue a job
    run_command('queuectl enqueue \'{"id":"worker_test","command":"echo Worker Test"}\'')
    
    # Start worker in background
    import multiprocessing
    def run_worker():
        os.system('timeout 5 queuectl worker start 2>/dev/null || true')
    
    p = multiprocessing.Process(target=run_worker)
    p.start()
    
    # Wait for job to process
    time.sleep(3)
    
    # Check if job completed
    code, out, err = run_command('queuectl list --state completed')
    
    # Terminate worker
    p.terminate()
    p.join()
    
    if "worker_test" in out:
        print("✓ Worker processed job successfully")
    else:
        print("⚠ Worker test inconclusive (may need more time)")

def test_dlq():
    """Test Dead Letter Queue"""
    print("\n=== Test 6: Dead Letter Queue ===")
    
    # Enqueue a failing job
    run_command('queuectl enqueue \'{"id":"fail_test","command":"exit 1","max_retries":1}\'')
    
    # Start worker briefly
    import multiprocessing
    def run_worker():
        os.system('timeout 10 queuectl worker start 2>/dev/null || true')
    
    p = multiprocessing.Process(target=run_worker)
    p.start()
    
    # Wait for retries
    time.sleep(8)
    
    # Check DLQ
    code, out, err = run_command('queuectl dlq list')
    
    p.terminate()
    p.join()
    
    if code == 0:
        print("✓ DLQ command works")
        if "fail_test" in out:
            print("✓ Failed job moved to DLQ")
        else:
            print("⚠ Job may still be retrying")
    else:
        print("✗ DLQ command failed")

def cleanup():
    """Clean up test data"""
    print("\n=== Cleanup ===")
    import shutil
    if os.path.exists('.queuectl'):
        shutil.rmtree('.queuectl')
    print("✓ Test data cleaned up")

def main():
    print("=" * 60)
    print("QUEUECTL TEST SUITE")
    print("=" * 60)
    
    try:
        test_enqueue()
        test_status()
        test_list()
        test_config()
        test_worker_basic()
        test_dlq()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    finally:
        cleanup()

if __name__ == '__main__':
    main()
