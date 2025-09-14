"""
Usage examples for custom mailbox models that prevent email deletion.

This module demonstrates how to use the custom transport classes and mailbox models
to process emails without deleting them from the IMAP server.
"""
from mailbox_custom.models import NoDeleteMailbox, MarkAsReadMailbox, UnreadOnlyMailbox
from django_mailbox.models import Mailbox
import logging

logger = logging.getLogger(__name__)


def example_1_basic_usage():
    """
    Example 1: Basic usage of NoDeleteMailbox
    
    This example shows how to replace regular Mailbox usage with NoDeleteMailbox
    to prevent email deletion.
    """
    print("=== Example 1: Basic NoDeleteMailbox Usage ===")
    
    # OLD WAY (deletes emails):
    # mailbox = Mailbox.objects.get(name='my_imap_mailbox')
    
    # NEW WAY (preserves emails):
    try:
        mailbox = NoDeleteMailbox.objects.get(name='my_imap_mailbox')
        messages = list(mailbox.get_new_mail())
        
        print(f"Processed {len(messages)} messages without deletion")
        for msg in messages:
            print(f"  - {msg.subject} from {msg.from_header}")
            
    except NoDeleteMailbox.DoesNotExist:
        print("Mailbox 'my_imap_mailbox' not found")


def example_2_mark_as_read():
    """
    Example 2: Using MarkAsReadMailbox to track processed emails
    
    This example shows how to use MarkAsReadMailbox to mark emails as read
    instead of deleting them, making it easier to track which emails have been processed.
    """
    print("\n=== Example 2: MarkAsReadMailbox Usage ===")
    
    try:
        mailbox = MarkAsReadMailbox.objects.get(name='my_imap_mailbox')
        messages = list(mailbox.get_new_mail())
        
        print(f"Processed {len(messages)} messages and marked as read")
        for msg in messages:
            print(f"  - {msg.subject} from {msg.from_header}")
            
    except MarkAsReadMailbox.DoesNotExist:
        print("Mailbox 'my_imap_mailbox' not found")


def example_3_unread_only():
    """
    Example 3: Using UnreadOnlyMailbox to process only new emails
    
    This example shows how to use UnreadOnlyMailbox to process only unread emails,
    preventing reprocessing of already handled messages.
    """
    print("\n=== Example 3: UnreadOnlyMailbox Usage ===")
    
    try:
        mailbox = UnreadOnlyMailbox.objects.get(name='my_imap_mailbox')
        messages = list(mailbox.get_new_mail())
        
        print(f"Processed {len(messages)} unread messages")
        for msg in messages:
            print(f"  - {msg.subject} from {msg.from_header}")
            
    except UnreadOnlyMailbox.DoesNotExist:
        print("Mailbox 'my_imap_mailbox' not found")


def example_4_bulk_processing():
    """
    Example 4: Bulk processing multiple mailboxes
    
    This example shows how to process multiple mailboxes using different strategies.
    """
    print("\n=== Example 4: Bulk Processing ===")
    
    # Process all active NoDeleteMailboxes
    mailboxes = NoDeleteMailbox.objects.filter(active=True)
    total_messages = 0
    
    for mailbox in mailboxes:
        print(f"Processing {mailbox.name}...")
        try:
            messages = list(mailbox.get_new_mail())
            message_count = len(messages)
            total_messages += message_count
            print(f"  Processed {message_count} messages")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print(f"Total messages processed: {total_messages}")


def example_5_with_conditions():
    """
    Example 5: Processing emails with custom conditions
    
    This example shows how to use conditions to filter which emails get processed.
    """
    print("\n=== Example 5: Conditional Processing ===")
    
    def important_emails_only(message):
        """Only process emails marked as important or from specific senders."""
        subject = message.get('subject', '').lower()
        from_addr = message.get('from', '').lower()
        
        # Process if subject contains 'urgent' or 'important'
        if 'urgent' in subject or 'important' in subject:
            return True
            
        # Process if from specific important senders
        important_senders = ['boss@company.com', 'alerts@system.com']
        if any(sender in from_addr for sender in important_senders):
            return True
            
        return False
    
    try:
        mailbox = NoDeleteMailbox.objects.get(name='my_imap_mailbox')
        messages = list(mailbox.get_new_mail(condition=important_emails_only))
        
        print(f"Processed {len(messages)} important messages")
        for msg in messages:
            print(f"  - {msg.subject} from {msg.from_header}")
            
    except NoDeleteMailbox.DoesNotExist:
        print("Mailbox 'my_imap_mailbox' not found")


def example_6_monkey_patch_existing_code():
    """
    Example 6: Monkey patching existing code
    
    This example shows how to modify existing code that uses regular Mailbox
    without changing the existing codebase extensively.
    """
    print("\n=== Example 6: Monkey Patching ===")
    
    from mailbox_custom.transports import NoDeleteImapTransport
    
    def patched_get_connection(self):
        """Patched version that prevents deletion for IMAP connections."""
        if not self.uri:
            return None
        elif self.type == 'imap':
            conn = NoDeleteImapTransport(
                self.location,
                port=self.port if self.port else None,
                ssl=self.use_ssl,
                tls=self.use_tls,
                archive=self.archive,
                folder=self.folder
            )
            conn.connect(self.username, self.password)
            return conn
        else:
            # Use original method for non-IMAP
            return self._original_get_connection()
    
    # Apply the monkey patch
    if not hasattr(Mailbox, '_original_get_connection'):
        Mailbox._original_get_connection = Mailbox.get_connection
        Mailbox.get_connection = patched_get_connection
        print("Monkey patch applied - all IMAP mailboxes now use no-delete transport")
    else:
        print("Monkey patch already applied")


def example_7_django_signals():
    """
    Example 7: Using Django signals with custom mailboxes
    
    This example shows how to use Django signals to perform additional
    processing when messages are received.
    """
    print("\n=== Example 7: Django Signals ===")
    
    from django_mailbox.signals import message_received
    from django.dispatch import receiver
    
    @receiver(message_received)
    def handle_received_message(sender, message, **kwargs):
        """Handle received messages with custom logic."""
        print(f"Signal received: New message '{message.subject}' from {sender.name}")
        
        # Add custom processing here
        if 'urgent' in message.subject.lower():
            print("  -> Urgent message detected, sending notification")
            # send_urgent_notification(message)
        
        # Log message details
        logger.info(f"Processed message: {message.subject}")
    
    # Now when you process messages, the signal handler will be called
    try:
        mailbox = NoDeleteMailbox.objects.get(name='my_imap_mailbox')
        messages = list(mailbox.get_new_mail())
        print(f"Processed {len(messages)} messages with signal handling")
    except NoDeleteMailbox.DoesNotExist:
        print("Mailbox not found")


if __name__ == '__main__':
    """
    Run all examples (for demonstration purposes).
    
    In a real Django environment, you would call these functions from
    views, management commands, or other Django components.
    """
    example_1_basic_usage()
    example_2_mark_as_read()
    example_3_unread_only()
    example_4_bulk_processing()
    example_5_with_conditions()
    example_6_monkey_patch_existing_code()
    example_7_django_signals()
