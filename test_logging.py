#!/usr/bin/env python
"""
Test script to verify logging configuration with separate app and scheduler logs
Usage: python test_logging.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailwatcher.settings')
django.setup()

import logging

def test_logging():
    """Test logging configuration with separate app and scheduler logs"""
    
    # Get loggers for our key components
    mailbox_logger = logging.getLogger('mailbox_custom')
    scheduler_logger = logging.getLogger('apscheduler')
    root_logger = logging.getLogger()
    
    print("Testing logging configuration with separate app and scheduler logs...")
    print("=" * 60)
    
    # Test Mailbox logger (goes to app.log)
    print("1. Testing Mailbox Custom logger (→ app.log)...")
    mailbox_logger.info("Mailbox logger test - INFO level")
    mailbox_logger.warning("Mailbox logger test - WARNING level")
    mailbox_logger.error("Mailbox logger test - ERROR level")
    
    # Test Scheduler logger (goes to scheduler.log)
    print("2. Testing APScheduler logger (→ scheduler.log)...")
    scheduler_logger.info("Scheduler logger test - INFO level")
    scheduler_logger.warning("Scheduler logger test - WARNING level")
    scheduler_logger.error("Scheduler logger test - ERROR level")
    
    # Test Root logger (goes to app.log)
    print("3. Testing Root logger (→ app.log)...")
    root_logger.info("Root logger test - INFO level")
    root_logger.warning("Root logger test - WARNING level")
    root_logger.error("Root logger test - ERROR level")
    
    # Test Error logging (goes to errors.log)
    print("4. Testing Error logging (→ errors.log)...")
    try:
        raise ValueError("Test error for logging")
    except ValueError as e:
        mailbox_logger.error(f"Test error logged: {e}")
        scheduler_logger.exception("Test exception with traceback")
    
    print("=" * 60)
    print("Logging test completed!")
    
    # Check if log files were created
    logs_dir = Path('logs')
    if logs_dir.exists():
        print(f"\nLog files created in: {logs_dir.absolute()}")
        expected_files = ['app.log', 'scheduler.log', 'errors.log']
        for log_file in expected_files:
            file_path = logs_dir / log_file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  {log_file}: {size} bytes")
            else:
                print(f"  {log_file}: Not found")
        
        # Show any other log files
        other_files = [f for f in logs_dir.glob('*.log') if f.name not in expected_files]
        if other_files:
            print("\nOther log files:")
            for log_file in other_files:
                size = log_file.stat().st_size
                print(f"  - {log_file.name}: {size} bytes")
    else:
        print("\nWarning: logs directory not found!")

if __name__ == '__main__':
    test_logging()
