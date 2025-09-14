from .base_endpoint import BaseEndpoint
import os
import json
from datetime import datetime


class Notification(BaseEndpoint):

    def send(self, message_body: dict = {}, timeout=30):
        '''
        send function to call the call_api functions.

        Args:
            message_body: The message for sending notifications.

        Returns:
            Send the notifications.
        '''

        headers = {}
        notif_url = os.getenv("NOTIF_URL")
        
        # Skip notification if URL is not configured
        if not notif_url:
            return False, "NOTIF_URL environment variable not set"
            
        # data to be sent to api
        try:
            data = {
                "username": os.getenv("NOTIF_USERNAME"),
                "password": os.getenv("NOTIF_PASSWORD")
            }
            # calling the login endpoint with the username and password
            r = BaseEndpoint.call_api(notif_url, path='/api/v1/account/login/', method='post', body=data, timeout=timeout)
            # If user can login and has the access token then he/she can send the notification
            if r and r.get('access'):
                headers = {'Authorization': 'Bearer ' + r['access']}
                response = BaseEndpoint.call_api(notif_url, path='/api/v1/notifications/', method='post', headers=headers,
                                             body=message_body, timeout=timeout)
                if response:
                    return True, response
                else:
                    return False, "Failed to send notification"
            return False, "You don't have access token"
        # Raise error if the variable is not set
        except KeyError:
            # Terminate from the script
            return False, "There is an error for environment variables 'NOTIF_URL','NOTIF_USERNAME', 'NOTIF_PASSWORD'."

    
    def send_email_alert(self, email_data=None, mailbox_name=None, message_count=0):
        '''
        Send email notification with dynamic content based on incoming email data.
        
        Args:
            email_data: Email message object or dict containing email information
            mailbox_name: Name of the mailbox that received emails
            message_count: Number of new emails detected
            
        Returns:
            Tuple of (success: bool, response/error_message)
        '''
        # Get notification tag from environment variable, fallback to 'mailbox'
        notification_tag = os.getenv("NOTIFICATION_TAG", "mailbox")
        
        # Generate dynamic notification body based on email data
        if email_data and hasattr(email_data, 'from_header'):
            # Extract email information from django-mailbox Message object
            sender_email = getattr(email_data, 'from_header', 'Unknown Sender')
            subject = getattr(email_data, 'subject', 'No Subject')
            
            # Create professional body message
            body_message = f"You have received a new email in {mailbox_name} from {sender_email}."
            
            # Create extra metadata JSON
            extra_data = {
                "alertname": f"New email in {mailbox_name}",
                "mailbox": mailbox_name,
                "sender": sender_email,
                "subject": subject,
                "message_count": message_count
            }
            
            # Add optional fields if available
            if hasattr(email_data, 'processed'):
                extra_data["processed_time"] = email_data.processed.isoformat() if email_data.processed else None
            if hasattr(email_data, 'message_id'):
                extra_data["message_id"] = getattr(email_data, 'message_id', None)
            if hasattr(email_data, 'in_reply_to'):
                extra_data["in_reply_to"] = getattr(email_data, 'in_reply_to', None)
                
        elif isinstance(email_data, dict):
            # Handle email data as dictionary
            sender_email = email_data.get('from', 'Unknown Sender')
            subject = email_data.get('subject', 'No Subject')
            
            body_message = f"You have received a new email in {mailbox_name} from {sender_email}."
            
            extra_data = {
                "alertname": f"New email in {mailbox_name}",
                "mailbox": mailbox_name,
                "sender": sender_email,
                "subject": subject,
                "message_count": message_count,
                **email_data  # Include any additional email data
            }
        else:
            # Fallback for when no email data is provided
            body_message = f"You have received {message_count} new email(s) in {mailbox_name}."
            
            extra_data = {
                "alertname": f"New emails in {mailbox_name}",
                "mailbox": mailbox_name,
                "message_count": message_count
            }
        
        # Build the notification payload
        notification_body = {
            "body": body_message,
            "tag": notification_tag,
            "extra": extra_data
        }
        
        return self.send(notification_body)
