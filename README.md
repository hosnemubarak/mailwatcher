# MailWatcher - Django Email Processing System

A Django application that processes emails from IMAP servers without deleting them. Built on django-mailbox with custom transport classes and automated scheduling.

## Quick Start with Docker

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd mailwatcher
   cp .env.example .env
   ```

2. **Configure your email settings** in `.env`:
   ```bash
   # Required: Update these with your notification service
   NOTIF_URL=https://your-notification-service.com
   NOTIF_USERNAME=your_notification_username
   NOTIF_PASSWORD=your_notification_password
   
   # Optional: Adjust these as needed
   EMAIL_FETCH_INTERVAL=60
   DEBUG=True
   ```

3. **Run with Docker**:
   ```bash
   docker-compose up -d
   ```

4. **Setup your mailboxes**:
   - Visit http://localhost:8000/admin
   - Login with admin/admin
   - Add your IMAP mailboxes using format: `imap+ssl://username:password@imap.server.com:993`

That's it! The system will automatically process emails every 60 seconds.

## Manual Setup (Without Docker)

If you prefer to run without Docker:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py start_email_scheduler
```

## Features

- **No-Delete Email Processing**: Process emails while keeping them on the server
- **Multiple Processing Modes**: Choose how emails are handled after processing
- **Automated Scheduling**: Run email processing every minute with APScheduler
- **Django Admin Integration**: Manage mailboxes through the admin interface
- **Comprehensive Logging**: Separate logs for application and scheduler activities

## Email Processing Modes

- **No-Delete Mode** (Default): Process all emails without deleting them
- **Mark-as-Read Mode**: Process emails and mark them as read
- **Unread-Only Mode**: Process only unread emails

## Configuration

Key environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `NOTIF_URL` | Notification service URL | Required |
| `NOTIF_USERNAME` | Notification username | Required |
| `NOTIF_PASSWORD` | Notification password | Required |
| `EMAIL_FETCH_INTERVAL` | Seconds between fetches | 60 |
| `DEBUG` | Enable debug mode | True |

## Commands

```bash
# Process emails manually
docker-compose exec app python manage.py getmail_nodelete

# Start scheduler manually
docker-compose exec app python manage.py start_email_scheduler

# View logs
docker-compose logs -f app
```

## IMAP Mailbox Setup

In Django admin, create mailboxes with URI format:
```
imap+ssl://username:password@imap.server.com:993
```

## Troubleshooting

- Check logs: `docker-compose logs app`
- Restart services: `docker-compose restart`
- Reset database: `docker-compose down -v && docker-compose up -d`

For detailed documentation and advanced usage, see the original comprehensive README in the repository history.
