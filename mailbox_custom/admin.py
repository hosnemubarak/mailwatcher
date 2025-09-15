from django.contrib import admin
from django_mailbox.admin import MailboxAdmin
from .models import UnreadOnlyNoMarkMailbox


@admin.register(UnreadOnlyNoMarkMailbox)
class UnreadOnlyNoMarkMailboxAdmin(MailboxAdmin):
    """Admin interface for UnreadOnlyNoMarkMailbox."""
    pass
