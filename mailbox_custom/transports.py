"""
Custom IMAP transport classes that prevent email deletion.

These transport classes extend django-mailbox's ImapTransport to provide
non-destructive email processing options.
"""
import logging
from django_mailbox.transports.imap import ImapTransport
from django_mailbox.transports.base import MessageParseError
from django_mailbox.models import Message

logger = logging.getLogger(__name__)


class NoDeleteImapTransport(ImapTransport):
    """
    Custom IMAP transport that prevents email deletion.
    
    This transport processes emails normally but skips the deletion step,
    leaving all emails in the inbox after processing.
    
    Usage:
        Use this transport when you want to process emails multiple times
        or when you need to preserve all emails on the server.
    """
    
    def get_message(self, condition=None):
        """
        Fetch and process messages without deleting them from the server.
        
        This method is identical to the parent class except it removes
        the email deletion logic (marking as deleted and expunging).
        """
        logger.info("Starting NoDeleteImapTransport message processing")
        
        try:
            message_ids = self._get_all_message_ids()
            logger.debug(f"Retrieved {len(message_ids) if message_ids else 0} message IDs")
        except Exception as e:
            logger.error(f"Failed to retrieve message IDs: {e}")
            return

        if not message_ids:
            logger.info("No messages found to process")
            return

        # Limit the uids to the small ones if we care about that
        if self.max_message_size:
            original_count = len(message_ids)
            try:
                message_ids = self._get_small_message_ids(message_ids)
                logger.debug(f"Filtered messages by size: {original_count} -> {len(message_ids)}")
            except Exception as e:
                logger.error(f"Failed to filter messages by size: {e}")

        if self.archive:
            try:
                typ, folders = self.server.list(pattern=self.archive)
                if folders[0] is None:
                    logger.info(f"Creating archive folder: {self.archive}")
                    self.server.create(self.archive)
                else:
                    logger.debug(f"Archive folder exists: {self.archive}")
            except Exception as e:
                logger.error(f"Failed to handle archive folder {self.archive}: {e}")

        processed_count = 0
        error_count = 0
        
        for uid in message_ids:
            try:
                logger.debug(f"Processing message UID: {uid}")
                typ, msg_contents = self.server.uid('fetch', uid, '(RFC822)')
                if not msg_contents:
                    logger.warning(f"No content found for message UID: {uid}")
                    continue
                    
                try:
                    message = self.get_email_from_bytes(msg_contents[0][1])
                    logger.debug(f"Successfully parsed message UID: {uid}")
                except TypeError as e:
                    logger.warning(f"Message UID {uid} was deleted by another process: {e}")
                    continue

                if condition and not condition(message):
                    logger.debug(f"Message UID {uid} filtered out by condition")
                    continue

                yield message
                processed_count += 1
                logger.debug(f"Successfully yielded message UID: {uid}")
                
            except MessageParseError as e:
                error_count += 1
                logger.error(f"Failed to parse message UID {uid}: {e}")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"Unexpected error processing message UID {uid}: {e}")
                continue

            if self.archive:
                try:
                    self.server.uid('copy', uid, self.archive)
                    logger.debug(f"Copied message UID {uid} to archive: {self.archive}")
                except Exception as e:
                    logger.error(f"Failed to copy message UID {uid} to archive: {e}")

            # DELETION PREVENTION: The following lines are commented out
            # to prevent email deletion from the server
            # self.server.uid('store', uid, "+FLAGS", "(\\Deleted)")
            
        # DELETION PREVENTION: expunge() is commented out to prevent
        # permanent deletion of emails marked as deleted
        # self.server.expunge()
        
        logger.info(f"NoDeleteImapTransport completed: {processed_count} messages processed, {error_count} errors")
        return


class MarkAsReadImapTransport(ImapTransport):
    """
    Alternative IMAP transport that marks emails as read instead of deleting them.
    
    This transport helps distinguish between processed and unprocessed emails
    while keeping them in the inbox. Processed emails will appear as "read"
    in email clients.
    
    Usage:
        Use this transport when you want to track which emails have been
        processed without deleting them from the server.
    """
    
    def get_message(self, condition=None):
        """
        Fetch and process messages, marking them as read instead of deleting.
        
        This method processes emails and marks them with the \\Seen flag
        instead of the \\Deleted flag, so they appear as read in email clients.
        """
        logger.info("Starting MarkAsReadImapTransport message processing")
        
        try:
            message_ids = self._get_all_message_ids()
            logger.debug(f"Retrieved {len(message_ids) if message_ids else 0} message IDs")
        except Exception as e:
            logger.error(f"Failed to retrieve message IDs: {e}")
            return

        if not message_ids:
            logger.info("No messages found to process")
            return

        # Limit the uids to the small ones if we care about that
        if self.max_message_size:
            original_count = len(message_ids)
            try:
                message_ids = self._get_small_message_ids(message_ids)
                logger.debug(f"Filtered messages by size: {original_count} -> {len(message_ids)}")
            except Exception as e:
                logger.error(f"Failed to filter messages by size: {e}")

        if self.archive:
            try:
                typ, folders = self.server.list(pattern=self.archive)
                if folders[0] is None:
                    logger.info(f"Creating archive folder: {self.archive}")
                    self.server.create(self.archive)
                else:
                    logger.debug(f"Archive folder exists: {self.archive}")
            except Exception as e:
                logger.error(f"Failed to handle archive folder {self.archive}: {e}")

        processed_count = 0
        marked_count = 0
        error_count = 0
        
        for uid in message_ids:
            try:
                logger.debug(f"Processing message UID: {uid}")
                typ, msg_contents = self.server.uid('fetch', uid, '(RFC822)')
                if not msg_contents:
                    logger.warning(f"No content found for message UID: {uid}")
                    continue
                    
                try:
                    message = self.get_email_from_bytes(msg_contents[0][1])
                    logger.debug(f"Successfully parsed message UID: {uid}")
                except TypeError as e:
                    logger.warning(f"Message UID {uid} was deleted by another process: {e}")
                    continue

                if condition and not condition(message):
                    logger.debug(f"Message UID {uid} filtered out by condition")
                    continue

                yield message
                processed_count += 1
                logger.debug(f"Successfully yielded message UID: {uid}")
                
            except MessageParseError as e:
                error_count += 1
                logger.error(f"Failed to parse message UID {uid}: {e}")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"Unexpected error processing message UID {uid}: {e}")
                continue

            if self.archive:
                try:
                    self.server.uid('copy', uid, self.archive)
                    logger.debug(f"Copied message UID {uid} to archive: {self.archive}")
                except Exception as e:
                    logger.error(f"Failed to copy message UID {uid} to archive: {e}")

            # Mark as read instead of deleting
            try:
                self.server.uid('store', uid, "+FLAGS", "(\\Seen)")
                marked_count += 1
                logger.debug(f"Marked message UID {uid} as read")
            except Exception as e:
                logger.error(f"Failed to mark message UID {uid} as read: {e}")
            
        # No expunge call - emails remain in inbox but are marked as read
        logger.info(f"MarkAsReadImapTransport completed: {processed_count} messages processed, {marked_count} marked as read, {error_count} errors")
        return


class UnreadOnlyImapTransport(ImapTransport):
    """
    IMAP transport that only processes unread emails and marks them as read.
    
    This transport fetches only unread emails, processes them, and marks them
    as read. This prevents reprocessing of already handled emails.
    
    Usage:
        Use this transport when you want to process only new/unread emails
        and avoid reprocessing emails that have already been handled.
    """
    
    def _get_unread_message_ids(self):
        """Fetch only unread message UIDs."""
        logger.debug("Searching for unread messages")
        try:
            # Search for unseen (unread) messages
            response, message_ids = self.server.uid('search', None, 'UNSEEN')
            message_id_string = message_ids[0].strip()
            
            if message_id_string:
                ids = message_id_string.decode().split(' ')
                logger.debug(f"Found {len(ids)} unread messages")
                return ids
            else:
                logger.debug("No unread messages found")
                return []
        except Exception as e:
            logger.error(f"Failed to search for unread messages: {e}")
            return []
    
    def get_message(self, condition=None):
        """
        Fetch and process only unread messages, marking them as read.
        
        This method only processes emails that haven't been read yet,
        preventing duplicate processing of the same emails.
        """
        logger.info("Starting UnreadOnlyImapTransport message processing")
        
        # Get only unread messages instead of all messages
        message_ids = self._get_unread_message_ids()

        if not message_ids:
            logger.info("No unread messages found")
            return

        # Limit the uids to the small ones if we care about that
        if self.max_message_size:
            original_count = len(message_ids)
            try:
                message_ids = self._get_small_message_ids(message_ids)
                logger.debug(f"Filtered messages by size: {original_count} -> {len(message_ids)}")
            except Exception as e:
                logger.error(f"Failed to filter messages by size: {e}")

        if self.archive:
            try:
                typ, folders = self.server.list(pattern=self.archive)
                if folders[0] is None:
                    logger.info(f"Creating archive folder: {self.archive}")
                    self.server.create(self.archive)
                else:
                    logger.debug(f"Archive folder exists: {self.archive}")
            except Exception as e:
                logger.error(f"Failed to handle archive folder {self.archive}: {e}")

        processed_count = 0
        marked_count = 0
        error_count = 0
        
        for uid in message_ids:
            try:
                logger.debug(f"Processing unread message UID: {uid}")
                typ, msg_contents = self.server.uid('fetch', uid, '(RFC822)')
                if not msg_contents:
                    logger.warning(f"No content found for message UID: {uid}")
                    continue
                    
                try:
                    message = self.get_email_from_bytes(msg_contents[0][1])
                    logger.debug(f"Successfully parsed message UID: {uid}")
                except TypeError as e:
                    logger.warning(f"Message UID {uid} was deleted by another process: {e}")
                    continue

                if condition and not condition(message):
                    logger.debug(f"Message UID {uid} filtered out by condition")
                    continue

                yield message
                processed_count += 1
                logger.debug(f"Successfully yielded message UID: {uid}")
                
            except MessageParseError as e:
                error_count += 1
                logger.error(f"Failed to parse message UID {uid}: {e}")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"Unexpected error processing message UID {uid}: {e}")
                continue

            if self.archive:
                try:
                    self.server.uid('copy', uid, self.archive)
                    logger.debug(f"Copied message UID {uid} to archive: {self.archive}")
                except Exception as e:
                    logger.error(f"Failed to copy message UID {uid} to archive: {e}")

            # Mark as read to prevent reprocessing
            try:
                self.server.uid('store', uid, "+FLAGS", "(\\Seen)")
                marked_count += 1
                logger.debug(f"Marked message UID {uid} as read")
            except Exception as e:
                logger.error(f"Failed to mark message UID {uid} as read: {e}")
            
        logger.info(f"UnreadOnlyImapTransport completed: {processed_count} unread messages processed, {marked_count} marked as read, {error_count} errors")
        return

class UnreadOnlyNoMarkImapTransport(ImapTransport):
    """
    IMAP transport that only processes unread emails without marking them as read or deleting them.
    
    This transport fetches only unread emails and processes them, but leaves them
    completely unchanged on the server. Duplicate prevention is handled at the 
    Django model level using Message-ID headers.
    
    Usage:
        Use this transport when you want to process only new/unread emails
        but keep them in their original unread state on the server.
        Duplicates are prevented by django-mailbox's built-in Message-ID checking.
    """
    
    def _get_unread_message_ids(self):
        """Fetch only unread message UIDs."""
        logger.debug("Searching for unread messages")
        try:
            # Search for unseen (unread) messages
            response, message_ids = self.server.uid('search', None, 'UNSEEN')
            message_id_string = message_ids[0].strip()
            
            if message_id_string:
                ids = message_id_string.decode().split(' ')
                logger.debug(f"Found {len(ids)} unread messages")
                return ids
            else:
                logger.debug("No unread messages found")
                return []
        except Exception as e:
            logger.error(f"Failed to search for unread messages: {e}")
            return []
    
    def get_message(self, condition=None):
        """
        Fetch and process only unread messages without changing their status.
        
        This method only processes emails that haven't been read yet,
        but leaves them in their original unread state. Django-mailbox's
        built-in duplicate prevention using Message-ID headers prevents
        the same email from being saved multiple times to the database.
        """
        logger.info("Starting UnreadOnlyNoMarkImapTransport message processing")
        
        # Get only unread messages instead of all messages
        message_ids = self._get_unread_message_ids()

        if not message_ids:
            logger.info("No unread messages found")
            return

        # Limit the uids to the small ones if we care about that
        if self.max_message_size:
            original_count = len(message_ids)
            try:
                message_ids = self._get_small_message_ids(message_ids)
                logger.debug(f"Filtered messages by size: {original_count} -> {len(message_ids)}")
            except Exception as e:
                logger.error(f"Failed to filter messages by size: {e}")

        if self.archive:
            try:
                typ, folders = self.server.list(pattern=self.archive)
                if folders[0] is None:
                    logger.info(f"Creating archive folder: {self.archive}")
                    self.server.create(self.archive)
                else:
                    logger.debug(f"Archive folder exists: {self.archive}")
            except Exception as e:
                logger.error(f"Failed to handle archive folder {self.archive}: {e}")

        processed_count = 0
        error_count = 0
        
        for uid in message_ids:
            try:
                logger.debug(f"Processing unread message UID: {uid}")
                # Use BODY.PEEK to fetch without marking as read
                typ, msg_contents = self.server.uid('fetch', uid, '(BODY.PEEK[])')
                if not msg_contents:
                    logger.warning(f"No content found for message UID: {uid}")
                    continue
                    
                try:
                    message = self.get_email_from_bytes(msg_contents[0][1])
                    logger.debug(f"Successfully parsed message UID: {uid}")
                except TypeError as e:
                    logger.warning(f"Message UID {uid} was deleted by another process: {e}")
                    continue

                if condition and not condition(message):
                    logger.debug(f"Message UID {uid} filtered out by condition")
                    continue

                # Check for duplicate Message-ID
                message_id = message.get('Message-ID')
                if message_id and Message.objects.filter(message_id=message_id).exists():
                    logger.debug(f"Message UID {uid} is a duplicate (Message-ID: {message_id}), skipping")
                    continue

                yield message
                processed_count += 1
                logger.debug(f"Successfully yielded message UID: {uid}")
                
            except MessageParseError as e:
                error_count += 1
                logger.error(f"Failed to parse message UID {uid}: {e}")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"Unexpected error processing message UID {uid}: {e}")
                continue

            if self.archive:
                try:
                    self.server.uid('copy', uid, self.archive)
                    logger.debug(f"Copied message UID {uid} to archive: {self.archive}")
                except Exception as e:
                    logger.error(f"Failed to copy message UID {uid} to archive: {e}")

            # NO MARKING AS READ - emails remain unread on the server
            # NO DELETION - emails remain in inbox unchanged
            
        logger.info(f"UnreadOnlyNoMarkImapTransport completed: {processed_count} unread messages processed (left unread), {error_count} errors")
        return
