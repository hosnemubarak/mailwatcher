import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class MailboxCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailbox_custom'
    
    def ready(self):
        """Called when Django starts up."""
        logger.info("MailboxCustom app is ready")
        logger.debug(f"Loaded app: {self.name} with auto field: {self.default_auto_field}")
