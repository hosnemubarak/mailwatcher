# Email Scheduler Setup with APScheduler

This guide explains how to set up automated email fetching using APScheduler to run every minute.

## Installation

1. **Install APScheduler**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Method 1: Using the Management Command

```bash
# Start scheduler with default 60-second intervals
python manage.py start_email_scheduler

# Start scheduler with custom interval (30 seconds)
python manage.py start_email_scheduler --interval 30

# Start scheduler without verbose output
python manage.py start_email_scheduler --no-verbose

# Start scheduler with 1-minute intervals (60 seconds)
python manage.py start_email_scheduler --interval 60
```

### Method 2: Using the Startup Script

```bash
# Simple startup (uses default 60-second intervals)
python start_scheduler.py

# With custom interval
python start_scheduler.py --interval 60

# Without verbose output
python start_scheduler.py --no-verbose
```

## Features

- **Automatic Email Fetching**: Runs `getmail_nodelete --transport-type unreadonly --verbose` at specified intervals
- **Graceful Shutdown**: Handles Ctrl+C and system signals properly
- **Error Handling**: Continues running even if individual fetch operations fail
- **Logging**: Comprehensive logging with timestamps
- **Initial Fetch**: Runs an immediate fetch when starting
- **Configurable Interval**: Default 60 seconds, customizable via command line

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--interval` | Interval in seconds between fetches | 60 |
| `--no-verbose` | Disable verbose output for email fetching | False (verbose enabled) |

## What It Does

1. **Starts APScheduler** with a blocking scheduler
2. **Runs initial email fetch** immediately upon startup
3. **Schedules recurring fetches** at the specified interval
4. **Uses UnreadOnly transport** to efficiently process only new emails
5. **Marks processed emails as read** to avoid reprocessing
6. **Provides detailed logging** for monitoring and debugging

## Example Output

```
Starting email scheduler with 60 second intervals
Running initial email fetch...
Starting email fetch at 2025-09-14 14:52:30
Using UnreadOnlyMailbox (only unread emails will be processed)
Processing mailbox: Tasmir
INFO:mailbox_custom.transports:No unread messages found
  Processed 0 messages from Tasmir
Completed! Total messages processed: 0
Email fetch completed at 2025-09-14 14:52:31
Scheduler started. Press Ctrl+C to stop.
```

## Production Deployment

### Running as a Service (Windows)

Create a batch file `start_email_service.bat`:
```batch
@echo off
cd /d "D:\office\mailwatcher"
call .venv\Scripts\activate
python start_scheduler.py
pause
```

### Running as a Service (Linux/systemd)

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
ExecStart=/path/to/mailwatcher/.venv/bin/python start_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable mailwatcher
sudo systemctl start mailwatcher
sudo systemctl status mailwatcher
```

### Running with Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "start_scheduler.py"]
```

## Monitoring

### Logs
The scheduler provides detailed logging with timestamps. Monitor the output to track:
- Email fetch attempts
- Number of messages processed
- Any errors or exceptions

### Health Checks
You can implement health checks by monitoring:
- Process status
- Log file timestamps
- Database activity

## Troubleshooting

### Common Issues

1. **Scheduler won't start**:
   - Check if APScheduler is installed: `pip list | grep APScheduler`
   - Verify Django settings are correct

2. **No emails being processed**:
   - Check if mailboxes exist and are active
   - Verify IMAP credentials and connection
   - Ensure there are unread emails to process

3. **High CPU usage**:
   - Consider increasing the interval (default 60 seconds)
   - Check for IMAP connection issues

### Stopping the Scheduler

- **Interactive mode**: Press `Ctrl+C`
- **Service mode**: Use system service commands
- **Process kill**: Find PID and use `kill` command

## Best Practices

1. **Start with longer intervals** (60+ seconds) to avoid overwhelming the email server
2. **Monitor logs regularly** to ensure proper operation
3. **Use verbose mode initially** for debugging, disable in production if not needed
4. **Set up proper logging rotation** for long-running instances
5. **Consider email server rate limits** when setting intervals
