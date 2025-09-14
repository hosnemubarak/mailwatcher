import logging
import signal
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start APScheduler to fetch emails every minute'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = BlockingScheduler()
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=getattr(settings, 'EMAIL_FETCH_INTERVAL', 60),
            help=f'Interval in seconds between email fetches (default: {getattr(settings, "EMAIL_FETCH_INTERVAL", 60)})'
        )
        parser.add_argument(
            '--no-verbose',
            action='store_true',
            help='Disable verbose output for email fetching'
        )
    
    def fetch_emails(self, verbose=True):
        """Function to fetch emails using the getmail_nodelete command"""
        try:
            self.stdout.write(
                self.style.SUCCESS(f'Starting email fetch at {self.get_current_time()}')
            )
            
            # Call the getmail_nodelete command
            if verbose:
                call_command('getmail_nodelete', transport_type='unreadonly', verbose=True)
            else:
                call_command('getmail_nodelete', transport_type='unreadonly')
                
            self.stdout.write(
                self.style.SUCCESS(f'Email fetch completed at {self.get_current_time()}')
            )
            
        except Exception as e:
            logger.error(f'Error fetching emails: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error fetching emails: {str(e)}')
            )
    
    def get_current_time(self):
        """Get current time as string"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.stdout.write(
            self.style.WARNING('Received shutdown signal. Stopping scheduler...')
        )
        self.scheduler.shutdown()
        sys.exit(0)
    
    def handle(self, *args, **options):
        interval = options['interval']
        verbose = not options['no_verbose']
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting email scheduler with {interval} second intervals')
        )
        
        # Add job to scheduler
        self.scheduler.add_job(
            func=self.fetch_emails,
            trigger=IntervalTrigger(seconds=interval),
            args=[verbose],
            id='email_fetch_job',
            name='Fetch emails from mailboxes',
            replace_existing=True
        )
        
        # Register shutdown function
        atexit.register(lambda: self.scheduler.shutdown())
        
        try:
            # Run initial fetch
            self.stdout.write(
                self.style.SUCCESS('Running initial email fetch...')
            )
            self.fetch_emails(verbose)
            
            # Start scheduler
            self.stdout.write(
                self.style.SUCCESS(f'Scheduler started. Press Ctrl+C to stop.')
            )
            self.scheduler.start()
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Scheduler stopped by user.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Scheduler error: {str(e)}')
            )
        finally:
            self.scheduler.shutdown()
