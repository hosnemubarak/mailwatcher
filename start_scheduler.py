#!/usr/bin/env python
"""
Startup script for MailWatcher Email Scheduler
Usage: python start_scheduler.py
"""
import os
import sys
import logging
import django
from django.core.management import execute_from_command_line

# Set up basic logging before Django setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting MailWatcher Email Scheduler")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailwatcher.settings')
        logger.debug("Django settings module set to 'mailwatcher.settings'")
        
        django.setup()
        logger.info("Django setup completed successfully")
        
        # Default arguments for the scheduler
        args = ['manage.py', 'start_email_scheduler']
        
        # Add any command line arguments passed to this script
        if len(sys.argv) > 1:
            args.extend(sys.argv[1:])
            logger.info(f"Added command line arguments: {sys.argv[1:]}")
        
        logger.info(f"Executing command: {' '.join(args)}")
        execute_from_command_line(args)
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        logger.exception("Detailed error information:")
        sys.exit(1)
