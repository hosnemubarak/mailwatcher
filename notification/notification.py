from .base_endpoint import BaseEndpoint
import os


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
        Send email notification with support for dynamic content.
        Currently uses static body but designed for future dynamic content.
        
        Args:
            email_data: Future parameter for dynamic email content
            mailbox_name: Name of the mailbox that received emails
            message_count: Number of new emails detected
            
        Returns:
            Tuple of (success: bool, response/error_message)
        '''
        # Static notification body as requested
        # TODO: Replace with dynamic content when needed
        notification_body = {
            "body": "body test",
            "tag": "mailbox",
            "extra": {
                "alertname": "Mailbox alert"
            }
        }
        
        # Future enhancement: Use dynamic content
        # if email_data:
        #     notification_body = {
        #         "body": f"New email from {email_data.get('from', 'Unknown')}: {email_data.get('subject', 'No Subject')}",
        #         "tag": "mailbox",
        #         "extra": {
        #             "alertname": f"New email in {mailbox_name}",
        #             "mailbox": mailbox_name,
        #             "count": message_count,
        #             "subject": email_data.get('subject', ''),
        #             "from": email_data.get('from', '')
        #         }
        #     }
        
        return self.send(notification_body)
