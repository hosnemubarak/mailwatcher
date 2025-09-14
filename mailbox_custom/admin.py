"""
Admin configuration for custom mailbox models.
"""
from django.contrib import admin
from django_mailbox.admin import MailboxAdmin
from .models import NoDeleteMailbox, MarkAsReadMailbox, UnreadOnlyMailbox


@admin.register(NoDeleteMailbox)
class NoDeleteMailboxAdmin(MailboxAdmin):
    """Admin interface for NoDeleteMailbox."""
    pass


@admin.register(MarkAsReadMailbox) 
class MarkAsReadMailboxAdmin(MailboxAdmin):
    """Admin interface for MarkAsReadMailbox."""
    pass


@admin.register(UnreadOnlyMailbox)
class UnreadOnlyMailboxAdmin(MailboxAdmin):
    """Admin interface for UnreadOnlyMailbox."""
    pass
