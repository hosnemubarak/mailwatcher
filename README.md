# MailWatcher - Django Email Processing System

A Django application that processes emails from IMAP servers without deleting them. Built on django-mailbox with custom transport classes and automated scheduling.

## Features

- **No-Delete Email Processing**: Process emails while keeping them on the server
- **Multiple Processing Modes**: Choose how emails are handled after processing
- **Automated Scheduling**: Run email processing every minute with APScheduler
- **Django Admin Integration**: Manage mailboxes through the admin interface
- **Comprehensive Logging**: Separate logs for application and scheduler activities
- **Environment-based Configuration**: Secure configuration using .env files

## Quick Start

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env with your settings
   notepad .env
   ```

3. **Add to Django settings**:
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django_mailbox',
       'mailbox_custom',
   ]
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

## Configuration

### Environment Variables (.env file)

Create a `.env` file in your project root with the following variables:

```bash
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Notification System (Required for email alerts)
NOTIF_URL=https://your-notification-service.com
NOTIF_USERNAME=your_notification_username
NOTIF_PASSWORD=your_notification_password

# Scheduler Settings
EMAIL_FETCH_INTERVAL=60
SCHEDULER_TIMEZONE=UTC

# Logging Configuration
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=180

# Media and Static Files
MEDIA_ROOT_PATH=media
STATIC_ROOT_PATH=staticfiles
```

### Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | Auto-generated | Yes |
| `NOTIF_URL` | Notification service URL | None | For notifications |
| `NOTIF_USERNAME` | Notification service username | None | For notifications |
| `NOTIF_PASSWORD` | Notification service password | None | For notifications |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | True |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | localhost,127.0.0.1 |
| `EMAIL_FETCH_INTERVAL` | Scheduler interval in seconds | 60 |
| `SCHEDULER_TIMEZONE` | Timezone for scheduler | UTC |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_RETENTION_DAYS` | Log file retention period | 180 |

### Database Configuration (Optional)

For production with PostgreSQL/MySQL, add:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mailwatcher
# or
DATABASE_URL=mysql://user:password@localhost:3306/mailwatcher
```

### Security Settings (Production)

For production deployment, add these security settings:
```bash
DEBUG=False
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Basic Usage

**Process all emails without deleting them:**
```bash
python manage.py getmail_nodelete
```

**Start automated processing every minute:**
```bash
python manage.py start_email_scheduler
```

## Email Processing Modes

### 1. No-Delete Mode (Default)
```bash
python manage.py getmail_nodelete
```
- Processes all emails from all active mailboxes
- Keeps all emails unchanged on the server
- Best for: Testing, development, data migration

### 2. Mark-as-Read Mode
```bash
python manage.py getmail_nodelete inbox support --transport-type markread
```
- Processes specific mailboxes only
- Marks emails as read instead of deleting them
- Best for: Production environments, tracking processed emails

### 3. Unread-Only Mode
```bash
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```
- Processes only unread emails from all mailboxes
- Marks processed emails as read
- Best for: Regular automation, performance optimization

## Automated Email Processing

### Start the Scheduler

**Basic startup (60-second intervals):**
```bash
python manage.py start_email_scheduler
```

**Custom interval:**
```bash
python manage.py start_email_scheduler --interval 30
```

**Without verbose output:**
```bash
python manage.py start_email_scheduler --no-verbose
```

### What the Scheduler Does

1. Runs an immediate email fetch when started
2. Schedules recurring fetches at specified intervals
3. Uses unread-only processing for efficiency
4. Provides detailed logging for monitoring
5. Handles shutdown signals gracefully

### Example Output
```
Starting email scheduler with 60 second intervals
Running initial email fetch...
Starting email fetch at 2025-09-14 14:52:30
Processing mailbox: Tasmir
  Processed 0 messages from Tasmir
Email fetch completed at 2025-09-14 14:52:31
Scheduler started. Press Ctrl+C to stop.
```

## IMAP Mailbox Setup

**URI Format:**
```
imap+ssl://username:password@imap.server.com:993
imap+ssl://username:password@imap.server.com:993?folder=INBOX&archive=Processed
```

**Supported Parameters:**
- `folder`: Which folder to read from (default: INBOX)
- `archive`: Folder to copy emails to before processing

## Django Settings

The application includes pre-configured settings for:
- Media file handling with WhiteNoise
- Separate logging for app and scheduler
- Email attachment storage organization

## Using in Code

### Method 1: Custom Mailbox Models
```python
from mailbox_custom.models import NoDeleteMailbox, MarkAsReadMailbox, UnreadOnlyMailbox

# Process without deleting
mailbox = NoDeleteMailbox.objects.get(name='my_mailbox')
messages = list(mailbox.get_new_mail())

# Process and mark as read
mailbox = MarkAsReadMailbox.objects.get(name='my_mailbox')
messages = list(mailbox.get_new_mail())

# Process only unread emails
mailbox = UnreadOnlyMailbox.objects.get(name='my_mailbox')
messages = list(mailbox.get_new_mail())
```

### Method 2: Monkey Patching Existing Code
```python
from django_mailbox.models import Mailbox
from mailbox_custom.transports import NoDeleteImapTransport

def patched_get_connection(self):
    if self.type == 'imap':
        conn = NoDeleteImapTransport(
            self.location,
            port=self.port,
            ssl=self.use_ssl,
            tls=self.use_tls,
            archive=self.archive,
            folder=self.folder
        )
        conn.connect(self.username, self.password)
        return conn
    return self._original_get_connection()

# Apply patch
Mailbox._original_get_connection = Mailbox.get_connection
Mailbox.get_connection = patched_get_connection
```

## Command Reference

### getmail_nodelete Command

**Basic syntax:**
```bash
python manage.py getmail_nodelete [mailbox_names] [options]
```

**Options:**
- `--transport-type`: Choose `nodelete`, `markread`, or `unreadonly`
- `--verbose`: Enable detailed output

**Examples:**
```bash
# Process all mailboxes (no deletion)
python manage.py getmail_nodelete

# Process specific mailboxes with read marking
python manage.py getmail_nodelete inbox support --transport-type markread

# Process only unread emails with verbose output
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

### start_email_scheduler Command

**Basic syntax:**
```bash
python manage.py start_email_scheduler [options]
```

**Options:**
- `--interval`: Seconds between fetches (default: 60)
- `--no-verbose`: Disable verbose output

## Production Deployment

### Windows Service
Create `start_email_service.bat`:
```batch
@echo off
cd /d "D:\office\mailwatcher"
call .venv\Scripts\activate
python manage.py start_email_scheduler
pause
```

### Linux systemd Service
Create `/etc/systemd/system/mailwatcher.service`:
```ini
[Unit]
Description=MailWatcher Email Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/mailwatcher
Environment=PATH=/path/to/mailwatcher/.venv/bin
ExecStart=/path/to/mailwatcher/.venv/bin/python manage.py start_email_scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mailwatcher
sudo systemctl start mailwatcher
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "start_email_scheduler"]
```

## Comparison with Standard django-mailbox

| Feature | Standard django-mailbox | MailWatcher |
|---------|------------------------|-------------|
| Email Processing | Full processing | Full processing |
| Database Storage | Messages stored | Messages stored |
| Signal Handling | Signals sent | Signals sent |
| Email Deletion | Always deletes | Configurable |
| Read Status Tracking | No tracking | Mark as read option |
| Unread-only Processing | Processes all | Unread-only option |
| Automated Scheduling | Manual only | Built-in scheduler |

## Troubleshooting

### Common Issues

**"Mailbox not found" errors:**
- Ensure mailbox exists and is active in Django admin
- Check mailbox name spelling

**IMAP connection errors:**
- Verify server settings and credentials
- Check network connectivity and firewall

**Duplicate message processing:**
- Use `unreadonly` transport to avoid reprocessing
- Use `markread` transport to track processed emails

**Scheduler won't start:**
- Check APScheduler installation: `pip list | grep APScheduler`
- Verify Django settings configuration

### Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mailbox_custom')
```

Log files are automatically created in the `logs/` directory:
- `app.log`: Django application logs
- `scheduler.log`: APScheduler logs
- `errors.log`: All error-level logs

## Best Practices

1. **Start with no-delete mode** for testing and setup
2. **Use mark-as-read mode** for production tracking
3. **Use unread-only mode** for regular automation
4. **Always use verbose output** in production for monitoring
5. **Set appropriate intervals** to avoid overwhelming email servers
6. **Monitor logs regularly** to ensure proper operation
7. **Test thoroughly** in development before production deployment

## Technical Details

The custom transport classes override the `get_message()` method from django-mailbox to modify deletion behavior:

**Original django-mailbox behavior:**
```python
self.server.uid('store', uid, "+FLAGS", "(\\Deleted)")
self.server.expunge()
```

**Custom implementations:**
- **NoDeleteImapTransport**: Skips deletion entirely
- **MarkAsReadImapTransport**: Replaces with `self.server.uid('store', uid, "+FLAGS", "(\\Seen)")`
- **UnreadOnlyImapTransport**: Uses `UNSEEN` search and marks as read

## License

This project extends django-mailbox and follows the same licensing terms.
