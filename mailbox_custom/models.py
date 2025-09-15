import logging
from django_mailbox.models import Mailbox
from .transports import UnreadOnlyNoMarkImapTransport

logger = logging.getLogger(__name__)


class UnreadOnlyNoMarkMailbox(Mailbox):
    """
    Custom Mailbox that only processes unread emails without marking them as read.
    
    This mailbox uses UnreadOnlyNoMarkImapTransport for IMAP connections,
    which only fetches unread emails without marking them as read after processing.
    This prevents reprocessing of already handled emails and keeps the emails unread.
    """
    
    def get_connection(self):
        """Returns the transport instance for this mailbox with unread-only and no-mark behavior."""
        logger.debug(f"Creating UnreadOnlyNoMarkMailbox connection for {self.name}")
        
        if not self.uri:
            logger.warning(f"No URI configured for mailbox {self.name}")
            return None
            
        elif self.type == 'imap':
            try:
                logger.info(f"Establishing UnreadOnlyNoMark IMAP connection for {self.name} at {self.location}")
                conn = UnreadOnlyNoMarkImapTransport(
                    self.location,
                    port=self.port if self.port else None,
                    ssl=self.use_ssl,
                    tls=self.use_tls,
                    archive=self.archive,
                    folder=self.folder
                )
                
                logger.debug(f"Connecting to IMAP server for {self.name} with user {self.username}")
                conn.connect(self.username, self.password)
                logger.info(f"Successfully connected UnreadOnlyNoMarkMailbox {self.name}")
                return conn
                
            except Exception as e:
                logger.error(f"Failed to create UnreadOnlyNoMark IMAP connection for {self.name}: {e}")
                raise
        else:
            logger.debug(f"Using default connection for non-IMAP mailbox {self.name} (type: {self.type})")
            # Fall back to default behavior for non-IMAP transports
            return super().get_connection()

    def get_new_mail(self, condition=None):
        """Override to add logging for mail retrieval."""
        logger.info(f"Starting mail retrieval for UnreadOnlyNoMarkMailbox {self.name}")
        try:
            messages = list(super().get_new_mail(condition))
            logger.info(f"Retrieved {len(messages)} messages from UnreadOnlyNoMarkMailbox {self.name}")
            return messages
        except Exception as e:
            logger.error(f"Error retrieving mail from UnreadOnlyNoMarkMailbox {self.name}: {e}")
            raise

    class Meta:
        proxy = True
        verbose_name = "Unread-Only No-Mark Mailbox"
        verbose_name_plural = "Unread-Only No-Mark Mailboxes"
