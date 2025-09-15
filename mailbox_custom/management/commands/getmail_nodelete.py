import logging
from django.core.management.base import BaseCommand, CommandError
from mailbox_custom.models import UnreadOnlyNoMarkMailbox
from notification.notification import Notification

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch unread mail without deleting from server or marking as read'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_service = Notification()
    
    def add_arguments(self, parser):
        parser.add_argument(
            'mailbox_names', 
            nargs='*', 
            type=str,
            help='Names of mailboxes to process (if not specified, all active mailboxes)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def send_email_notification(self, messages, mailbox_name):
        """Send notification for each new email with dynamic content"""
        if not messages:
            return
            
        # Send notification for each email individually
        for message in messages:
            try:
                success, response = self.notification_service.send_email_alert(
                    email_data=message,
                    mailbox_name=mailbox_name,
                    message_count=1
                )
                if success:
                    sender = getattr(message, 'from_header', 'Unknown Sender')
                    subject = getattr(message, 'subject', 'No Subject')
                    logger.info(f"Notification sent for email from {sender}: {subject}")
                else:
                    logger.warning(f"Failed to send notification for email in {mailbox_name}: {response}")
            except Exception as e:
                logger.error(f"Error sending notification for email in {mailbox_name}: {str(e)}")
        
        # Also send a summary notification if multiple emails
        if len(messages) > 1:
            try:
                success, response = self.notification_service.send_email_alert(
                    email_data=None,
                    mailbox_name=mailbox_name,
                    message_count=len(messages)
                )
                if success:
                    logger.info(f"Summary notification sent for {len(messages)} emails in {mailbox_name}")
                else:
                    logger.warning(f"Failed to send summary notification for {mailbox_name}: {response}")
            except Exception as e:
                logger.error(f"Error sending summary notification for {mailbox_name}: {str(e)}")

    def handle(self, *args, **options):
        mailbox_names = options.get('mailbox_names')
        verbose = options.get('verbose')
        
        logger.info(f"Starting getmail_nodelete command with verbose={verbose}")
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        # Use UnreadOnlyNoMarkMailbox (only processes unread emails without marking them as read)
        MailboxModel = UnreadOnlyNoMarkMailbox
        message = "Using UnreadOnlyNoMarkMailbox (only unread emails will be processed and not marked as read)"
        logger.info("Selected UnreadOnlyNoMarkMailbox transport")
        
        self.stdout.write(message)
        
        # Filter mailboxes
        try:
            if mailbox_names:
                logger.info(f"Filtering mailboxes by names: {mailbox_names}")
                mailboxes = MailboxModel.objects.filter(
                    name__in=mailbox_names, 
                    active=True
                )
                if not mailboxes.exists():
                    error_msg = f'No active mailboxes found with names: {mailbox_names}'
                    logger.error(error_msg)
                    raise CommandError(error_msg)
                logger.info(f"Found {mailboxes.count()} matching active mailboxes")
            else:
                logger.info("Processing all active mailboxes")
                mailboxes = MailboxModel.objects.filter(active=True)
                if not mailboxes.exists():
                    error_msg = 'No active mailboxes found'
                    logger.error(error_msg)
                    raise CommandError(error_msg)
                logger.info(f"Found {mailboxes.count()} active mailboxes")
        except Exception as e:
            logger.error(f"Error querying mailboxes: {e}")
            raise
        
        total_messages = 0
        successful_mailboxes = 0
        failed_mailboxes = 0
        
        for mailbox in mailboxes:
            logger.info(f"Processing mailbox: {mailbox.name} (ID: {mailbox.id})")
            self.stdout.write(f'Processing mailbox: {mailbox.name}')
            
            try:
                logger.debug(f"Getting new mail for mailbox {mailbox.name}")
                messages = list(mailbox.get_new_mail())
                message_count = len(messages)
                total_messages += message_count
                successful_mailboxes += 1
                
                logger.info(f"Successfully processed {message_count} messages from {mailbox.name}")
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  Processed {message_count} messages from {mailbox.name}'
                    )
                )
                
                self.send_email_notification(messages, mailbox.name)
                
                if verbose and messages:
                    logger.debug(f"Listing {len(messages)} messages from {mailbox.name}")
                    for i, msg in enumerate(messages, 1):
                        subject = getattr(msg, 'subject', 'No Subject')
                        from_header = getattr(msg, 'from_header', 'Unknown Sender')
                        logger.debug(f"Message {i}: {subject} (from: {from_header})")
                        self.stdout.write(f'    - {subject} (from: {from_header})')
                elif verbose:
                    logger.debug(f"No messages to display for {mailbox.name}")
                        
            except Exception as e:
                failed_mailboxes += 1
                error_msg = f'Error processing {mailbox.name}: {str(e)}'
                logger.error(error_msg)
                logger.exception(f"Detailed error for mailbox {mailbox.name}")
                
                self.stdout.write(
                    self.style.ERROR(f'  {error_msg}')
                )
        
        # Final summary
        summary_msg = f'Completed! Total messages processed: {total_messages}'
        stats_msg = f'Mailboxes: {successful_mailboxes} successful, {failed_mailboxes} failed'
        
        logger.info(f"{summary_msg}. {stats_msg}")
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{summary_msg}')
        )
        
        if failed_mailboxes > 0:
            self.stdout.write(
                self.style.WARNING(f'Warning: {failed_mailboxes} mailboxes failed to process')
            )
