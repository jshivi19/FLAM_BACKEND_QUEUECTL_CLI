#!/usr/bin/env python3
"""
Installation verification script for queuectl
Run this after installation to verify everything works
"""

import subprocess
import sys
import os
import time
import shutil

def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_command(name, cmd):
    """Test a single command"""
    print(f"Testing: {name}...", end=" ")
    success, stdout, stderr = run_command(cmd)
    
    if not success:
        print("FAILED" if sys.platform == 'win32' else "❌ FAILED")
        if stderr:
            print(f"  Error: {stderr[:100]}")
        return False
    
    print("PASSED" if sys.platform == 'win32' else "✅ PASSED")
    return True

def cleanup_test_data():
    """Clean up test data"""
    if os.path.exists('.queuectl'):
        shutil.rmtree('.queuectl')

def main():
    print("=" * 60)
    print("QUEUECTL INSTALLATION VERIFICATION")
    print("=" * 60)
    print()
    
    # Clean up any existing test data
    cleanup_test_data()
    
    tests = [
        ("queuectl command available", "queuectl --help"),
        ("status command", "queuectl status"),
        ("list command", "queuectl list"),
        ("config command", "queuectl config set max_retries 3"),
        ("enqueue via helper", 'python enqueue_job.py verify_test "echo test"'),
        ("list pending jobs", "queuectl list --state pending"),
    ]
    
    passed = 0
    failed = 0
    
    for name, cmd in tests:
        if test_command(name, cmd):
            passed += 1
        else:
            failed += 1
    
    # Cleanup
    cleanup_test_data()
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        checkmark = "OK" if sys.platform == 'win32' else "✅"
        print()
        print(f"{checkmark} All tests passed! QueueCTL is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run demo: python quick_demo.py")
        print("  2. Add jobs: python enqueue_job.py <id> <command>")
        print("  3. Start workers: queuectl worker start")
        print()
        if sys.platform == 'win32':
            print("Windows users: See WINDOWS_GUIDE.md for detailed instructions")
        return 0
    else:
        print()
        print("Some tests failed. Please check the installation.")
        print()
        print("Troubleshooting:")
        print("  1. Make sure you ran: pip install -e .")
        print("  2. Try running: python -m queuectl --help")
        print("  3. Check WINDOWS_GUIDE.md for Windows-specific help")
        return 1

if __name__ == '__main__':
    sys.exit(main())
