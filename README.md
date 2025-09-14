# MailWatcher - Django Mailbox with No-Delete IMAP Transport

This Django project implements custom IMAP transport classes that prevent email deletion from the server while preserving the complete django-mailbox processing workflow.

## Features

- **NoDeleteImapTransport**: Processes emails without deleting them from the server
- **MarkAsReadImapTransport**: Marks emails as read instead of deleting them
- **UnreadOnlyImapTransport**: Only processes unread emails and marks them as read
- **Custom Mailbox Models**: Easy-to-use proxy models for each transport type
- **Management Commands**: Command-line tools for processing emails
- **Django Admin Integration**: Admin interface for managing custom mailboxes

## Installation

1. **Install Dependencies**:
   ```bash
   pip install django django-mailbox
   ```

2. **Add to Django Settings**:
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django_mailbox',
       'mailbox_custom',  # Add this line
   ]
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

## Usage

### Method 1: Using Custom Mailbox Models

```python
from mailbox_custom.models import NoDeleteMailbox, MarkAsReadMailbox, UnreadOnlyMailbox

# Process emails without deleting them
mailbox = NoDeleteMailbox.objects.get(name='my_imap_mailbox')
messages = list(mailbox.get_new_mail())

# Process emails and mark as read
mailbox = MarkAsReadMailbox.objects.get(name='my_imap_mailbox')
messages = list(mailbox.get_new_mail())

# Process only unread emails
mailbox = UnreadOnlyMailbox.objects.get(name='my_imap_mailbox')
messages = list(mailbox.get_new_mail())
```

### Method 2: Using Management Commands

```bash
# Process all active mailboxes without deleting emails
python manage.py getmail_nodelete

# Process specific mailboxes with mark-as-read behavior
python manage.py getmail_nodelete mailbox1 mailbox2 --transport-type markread

# Process only unread emails with verbose output
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

### Method 3: Monkey Patching Existing Code

```python
from django_mailbox.models import Mailbox
from mailbox_custom.transports import NoDeleteImapTransport

def patched_get_connection(self):
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
        return self._original_get_connection()

# Apply monkey patch
Mailbox._original_get_connection = Mailbox.get_connection
Mailbox.get_connection = patched_get_connection
```

## Transport Classes

### NoDeleteImapTransport
- **Purpose**: Processes emails without deleting them from the server
- **Use Case**: When you want to preserve all emails on the server
- **Behavior**: Fetches and processes all emails, but skips deletion

### MarkAsReadImapTransport
- **Purpose**: Marks emails as read instead of deleting them
- **Use Case**: When you want to track which emails have been processed
- **Behavior**: Processes emails and marks them with the `\Seen` flag

### UnreadOnlyImapTransport
- **Purpose**: Only processes unread emails and marks them as read
- **Use Case**: When you want to avoid reprocessing already handled emails
- **Behavior**: Fetches only unread emails using `UNSEEN` search, then marks as read

## Mailbox Models

### NoDeleteMailbox
- Proxy model using `NoDeleteImapTransport`
- Available in Django admin as "No-Delete Mailbox"

### MarkAsReadMailbox
- Proxy model using `MarkAsReadImapTransport`
- Available in Django admin as "Mark-as-Read Mailbox"

### UnreadOnlyMailbox
- Proxy model using `UnreadOnlyImapTransport`
- Available in Django admin as "Unread-Only Mailbox"

## Configuration

### IMAP Mailbox URI Format
```
imap+ssl://username:password@imap.server.com:993
imap+ssl://username:password@imap.server.com:993?folder=INBOX&archive=Processed
```

### Supported URI Parameters
- `folder`: Specify which folder to read from (default: INBOX)
- `archive`: Specify folder to copy emails to before processing

## Examples

See `mailbox_custom/examples.py` for comprehensive usage examples including:
- Basic usage patterns
- Bulk processing multiple mailboxes
- Conditional email processing
- Django signals integration
- Monkey patching existing code

## Management Commands

### getmail_nodelete
Process emails using custom transport classes.

**Arguments**:
- `mailbox_names`: Optional list of mailbox names to process
- `--transport-type`: Choose transport type (`nodelete`, `markread`, `unreadonly`)
- `--verbose`: Enable verbose output

**Examples**:
```bash
# Process all active mailboxes without deleting
python manage.py getmail_nodelete

# Process specific mailboxes with mark-as-read
python manage.py getmail_nodelete inbox support --transport-type markread

# Process only unread emails with verbose output
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

## Comparison with Original django-mailbox

| Feature | Original django-mailbox | Custom Implementation |
|---------|------------------------|----------------------|
| Email Processing | ✅ Full processing | ✅ Full processing |
| Database Storage | ✅ Messages stored | ✅ Messages stored |
| Signal Handling | ✅ Signals sent | ✅ Signals sent |
| Email Deletion | ❌ Deletes from server | ✅ Configurable |
| Archive Support | ✅ Copies to archive folder | ✅ Copies to archive folder |
| Read Status Tracking | ❌ No tracking | ✅ Mark as read option |
| Unread-only Processing | ❌ Processes all emails | ✅ Unread-only option |

## Technical Details

The custom transport classes override the `get_message()` method from `django_mailbox.transports.imap.ImapTransport` to modify the email deletion behavior:

**Original Code (lines 136-137 in ImapTransport.get_message())**:
```python
self.server.uid('store', uid, "+FLAGS", "(\\Deleted)")
self.server.expunge()
```

**Custom Implementations**:
- **NoDeleteImapTransport**: Comments out both lines
- **MarkAsReadImapTransport**: Replaces with `self.server.uid('store', uid, "+FLAGS", "(\\Seen)")`
- **UnreadOnlyImapTransport**: Uses `UNSEEN` search and marks as read

## Troubleshooting

### Common Issues

1. **"Mailbox not found" errors**:
   - Ensure the mailbox exists and is active
   - Check the mailbox name spelling

2. **IMAP connection errors**:
   - Verify IMAP server settings and credentials
   - Check firewall and network connectivity

3. **Duplicate message processing**:
   - Use `UnreadOnlyImapTransport` to avoid reprocessing
   - Or use `MarkAsReadImapTransport` to track processed emails

### Logging

Enable logging to debug issues:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mailbox_custom')
```

## License

This project extends django-mailbox and follows the same licensing terms.
