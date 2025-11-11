#!/usr/bin/env python3
"""
Installation verification script for queuectl
Run this after installation to verify everything works
"""

import subprocess
import sys

def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_command(name, cmd, expected_in_output=None):
    """Test a single command"""
    print(f"Testing: {name}...", end=" ")
    success, stdout, stderr = run_command(cmd)
    
    if not success:
        print("❌ FAILED")
        print(f"  Error: {stderr}")
        return False
    
    if expected_in_output and expected_in_output not in stdout:
        print("❌ FAILED")
        print(f"  Expected '{expected_in_output}' in output")
        return False
    
    print("✅ PASSED")
    return True

def main():
    print("=" * 60)
    print("QUEUECTL INSTALLATION VERIFICATION")
    print("=" * 60)
    print()
    
    tests = [
        ("queuectl command available", "queuectl --help", "queuectl"),
        ("enqueue command", "queuectl enqueue --help", "Add a new job"),
        ("worker command", "queuectl worker --help", "Manage worker"),
        ("status command", "queuectl status --help", "Show summary"),
        ("list command", "queuectl list --help", "List jobs"),
        ("dlq command", "queuectl dlq --help", "Dead Letter"),
        ("config command", "queuectl config --help", "configuration"),
    ]
    
    passed = 0
    failed = 0
    
    for name, cmd, expected in tests:
        if test_command(name, cmd, expected):
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print()
        print("✅ All tests passed! QueueCTL is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run demo: python demo.py")
        print("  2. Read QUICKSTART.md for usage examples")
        print("  3. Start building your job workflows!")
        return 0
    else:
        print()
        print("❌ Some tests failed. Please check the installation.")
        print()
        print("Troubleshooting:")
        print("  1. Make sure you ran: pip install -e .")
        print("  2. Check that Python scripts directory is in PATH")
        print("  3. Try running: python -m queuectl --help")
        return 1

if __name__ == '__main__':
    sys.exit(main())
