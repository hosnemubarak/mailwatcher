"""
Custom mailbox models that use non-destructive IMAP transports.

These models extend django-mailbox's Mailbox model to use custom transport
classes that prevent email deletion from the server.
"""
import logging
from django_mailbox.models import Mailbox
from .transports import (
    NoDeleteImapTransport, 
    MarkAsReadImapTransport, 
    UnreadOnlyImapTransport,
    UnreadOnlyNoMarkImapTransport
)

logger = logging.getLogger(__name__)


class NoDeleteMailbox(Mailbox):
    """
    Custom Mailbox that prevents email deletion during processing.
    
    This mailbox uses NoDeleteImapTransport for IMAP connections,
    which processes emails without deleting them from the server.
    
    Usage:
        Use this when you want to preserve all emails on the server
        while still processing them through django-mailbox.
    """
    
    def get_connection(self):
        """Returns the transport instance for this mailbox with no-delete behavior."""
        logger.debug(f"Creating NoDeleteMailbox connection for {self.name}")
        
        if not self.uri:
            logger.warning(f"No URI configured for mailbox {self.name}")
            return None
            
        elif self.type == 'imap':
            try:
                logger.info(f"Establishing NoDelete IMAP connection for {self.name} at {self.location}")
                conn = NoDeleteImapTransport(
                    self.location,
                    port=self.port if self.port else None,
                    ssl=self.use_ssl,
                    tls=self.use_tls,
                    archive=self.archive,
                    folder=self.folder
                )
                
                logger.debug(f"Connecting to IMAP server for {self.name} with user {self.username}")
                conn.connect(self.username, self.password)
                logger.info(f"Successfully connected NoDeleteMailbox {self.name}")
                return conn
                
            except Exception as e:
                logger.error(f"Failed to create NoDelete IMAP connection for {self.name}: {e}")
                raise
        else:
            logger.debug(f"Using default connection for non-IMAP mailbox {self.name} (type: {self.type})")
            # Fall back to default behavior for non-IMAP transports
            return super().get_connection()

    def get_new_mail(self, condition=None):
        """Override to add logging for mail retrieval."""
        logger.info(f"Starting mail retrieval for NoDeleteMailbox {self.name}")
        try:
            messages = list(super().get_new_mail(condition))
            logger.info(f"Retrieved {len(messages)} messages from NoDeleteMailbox {self.name}")
            return messages
        except Exception as e:
            logger.error(f"Error retrieving mail from NoDeleteMailbox {self.name}: {e}")
            raise

    class Meta:
        proxy = True
        verbose_name = "No-Delete Mailbox"
        verbose_name_plural = "No-Delete Mailboxes"


class MarkAsReadMailbox(Mailbox):
    """
    Custom Mailbox that marks emails as read instead of deleting them.
    
    This mailbox uses MarkAsReadImapTransport for IMAP connections,
    which marks processed emails as read but keeps them on the server.
    """
    
    def get_connection(self):
        """Returns the transport instance for this mailbox with mark-as-read behavior."""
        logger.debug(f"Creating MarkAsReadMailbox connection for {self.name}")
        
        if not self.uri:
            logger.warning(f"No URI configured for mailbox {self.name}")
            return None
            
        elif self.type == 'imap':
            try:
                logger.info(f"Establishing MarkAsRead IMAP connection for {self.name} at {self.location}")
                conn = MarkAsReadImapTransport(
                    self.location,
                    port=self.port if self.port else None,
                    ssl=self.use_ssl,
                    tls=self.use_tls,
                    archive=self.archive,
                    folder=self.folder
                )
                
                logger.debug(f"Connecting to IMAP server for {self.name} with user {self.username}")
                conn.connect(self.username, self.password)
                logger.info(f"Successfully connected MarkAsReadMailbox {self.name}")
                return conn
                
            except Exception as e:
                logger.error(f"Failed to create MarkAsRead IMAP connection for {self.name}: {e}")
                raise
        else:
            logger.debug(f"Using default connection for non-IMAP mailbox {self.name} (type: {self.type})")
            # Fall back to default behavior for non-IMAP transports
            return super().get_connection()

    def get_new_mail(self, condition=None):
        """Override to add logging for mail retrieval."""
        logger.info(f"Starting mail retrieval for MarkAsReadMailbox {self.name}")
        try:
            messages = list(super().get_new_mail(condition))
            logger.info(f"Retrieved {len(messages)} messages from MarkAsReadMailbox {self.name}")
            return messages
        except Exception as e:
            logger.error(f"Error retrieving mail from MarkAsReadMailbox {self.name}: {e}")
            raise

    class Meta:
        proxy = True
        verbose_name = "Mark-as-Read Mailbox"
        verbose_name_plural = "Mark-as-Read Mailboxes"


class UnreadOnlyMailbox(Mailbox):
    """
    Custom Mailbox that only processes unread emails and marks them as read.
    
    This mailbox uses UnreadOnlyImapTransport for IMAP connections,
    which only fetches unread emails and marks them as read after processing.
    This prevents reprocessing of already handled emails.
    """
    
    def get_connection(self):
        """Returns the transport instance for this mailbox with unread-only behavior."""
        logger.debug(f"Creating UnreadOnlyMailbox connection for {self.name}")
        
        if not self.uri:
            logger.warning(f"No URI configured for mailbox {self.name}")
            return None
            
        elif self.type == 'imap':
            try:
                logger.info(f"Establishing UnreadOnly IMAP connection for {self.name} at {self.location}")
                conn = UnreadOnlyImapTransport(
                    self.location,
                    port=self.port if self.port else None,
                    ssl=self.use_ssl,
                    tls=self.use_tls,
                    archive=self.archive,
                    folder=self.folder
                )
                
                logger.debug(f"Connecting to IMAP server for {self.name} with user {self.username}")
                conn.connect(self.username, self.password)
                logger.info(f"Successfully connected UnreadOnlyMailbox {self.name}")
                return conn
                
            except Exception as e:
                logger.error(f"Failed to create UnreadOnly IMAP connection for {self.name}: {e}")
                raise
        else:
            logger.debug(f"Using default connection for non-IMAP mailbox {self.name} (type: {self.type})")
            # Fall back to default behavior for non-IMAP transports
            return super().get_connection()

    def get_new_mail(self, condition=None):
        """Override to add logging for mail retrieval."""
        logger.info(f"Starting mail retrieval for UnreadOnlyMailbox {self.name}")
        try:
            messages = list(super().get_new_mail(condition))
            logger.info(f"Retrieved {len(messages)} messages from UnreadOnlyMailbox {self.name}")
            return messages
        except Exception as e:
            logger.error(f"Error retrieving mail from UnreadOnlyMailbox {self.name}: {e}")
            raise

    class Meta:
        proxy = True
        verbose_name = "Unread-Only Mailbox"
        verbose_name_plural = "Unread-Only Mailboxes"


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
