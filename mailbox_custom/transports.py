import logging
from django_mailbox.transports.imap import ImapTransport
from django_mailbox.transports.base import MessageParseError
from django_mailbox.models import Message

logger = logging.getLogger(__name__)


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
        but leaves them in their original unread state. Duplicate prevention
        is now per-mailbox, allowing the same Message-ID to exist across
        different mailboxes while preventing duplicates within the same mailbox.
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

                # Check for duplicate Message-ID within the same mailbox only
                message_id = message.get('Message-ID')
                if message_id:
                    # Get the current mailbox instance from the transport's mailbox attribute
                    current_mailbox = getattr(self, 'mailbox', None)
                    if current_mailbox and Message.objects.filter(
                        message_id=message_id, 
                        mailbox=current_mailbox
                    ).exists():
                        logger.debug(f"Message UID {uid} is a duplicate in mailbox '{current_mailbox.name}' (Message-ID: {message_id}), skipping")
                        continue
                    elif not current_mailbox:
                        logger.warning(f"No mailbox reference found in transport, using global duplicate check for Message-ID: {message_id}")
                        if Message.objects.filter(message_id=message_id).exists():
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
