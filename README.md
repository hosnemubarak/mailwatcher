# MailWatcher - Django Email Processing System

A Django application that processes unread emails from IMAP servers without modifying them. Built on django-mailbox with a custom transport class and automated scheduling.

## Quick Start with Docker

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd mailwatcher
   cp .env.example .env
   ```

2. **Configure your email settings** in `.env`:
   ```bash
      # Django Configuration
      DEBUG=True
      SECRET_KEY=your-secret-key-here
      ALLOWED_HOSTS=localhost,127.0.0.1

      # Notification System Settings
      NOTIF_URL=https://your-notification-service.com
      NOTIF_USERNAME=your_notification_username
      NOTIF_PASSWORD=your_notification_password
      NOTIFICATION_TAG=mailbox

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

3. **Run with Docker**:
   ```bash
   docker-compose up -d
   ```

4. **Setup your mailboxes**:
   - Visit http://localhost:8000/
   - Login with admin/admin
   - Add your IMAP mailboxes using the URI format below

## 📬 IMAP Mailbox Setup

Connect Django Mailbox to any IMAP server using a URI format:

**Example:**
```
imap+ssl://youremailaddress%40gmail.com:1234@imap.gmail.com
```
```
imap+ssl://youremailaddress%40gmail.com:1234@imap.gmail.com?folder=MyFolder&archive=Archived
```

**URI Parts:**
- `imap+ssl://` → IMAP with SSL encryption
- `youremailaddress%40gmail.com` → your email address (@ encoded as %40)
- `1234` → your email password
- `imap.gmail.com` → IMAP server hostname
- `?folder=MyFolder` (optional) → specific folder to monitor (default: INBOX)
- `&archive=Archived` (optional) → folder to move processed emails

**⚠️ URL Encoding Required:**
Some characters must be encoded in the URI: @ → %40, # → %23, : → %3A, & → %26

That's it! The system will automatically process unread emails every 60 seconds without modifying them on the server.

## Manual Setup (Without Docker)

If you prefer to run without Docker:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py start_email_scheduler
```

## Features

- **Unread-Only Processing**: Process only unread emails from the server
- **Non-Destructive**: Emails remain unread and unchanged on the server
- **Duplicate Prevention**: Built-in Message-ID checking prevents duplicate processing
- **Automated Scheduling**: Run email processing every minute with APScheduler
- **Django Admin Integration**: Manage mailboxes through the admin interface
- **Comprehensive Logging**: Separate logs for application and scheduler activities
- **Notification System**: Dynamic email notifications with full metadata

## Email Processing Behavior

The system uses **UnreadOnlyNoMarkMailbox** which:
- Processes only unread emails from IMAP servers
- Leaves emails in their original unread state
- Prevents duplicate processing using Message-ID headers
- Does not delete or modify emails on the server

## Commands

```bash
# Process emails manually
docker-compose exec app python manage.py getmail_nodelete

# Start scheduler manually
docker-compose exec app python manage.py start_email_scheduler

# View logs
docker-compose logs -f app
```

## Troubleshooting

- Check logs: `docker-compose logs app`
- Restart services: `docker-compose restart`
- Reset database: `docker-compose down -v && docker-compose up -d`

For detailed command documentation, see `COMMANDS.md`.
