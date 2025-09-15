# MailWatcher Commands Documentation

This document explains how to use the two main commands in MailWatcher: `start_email_scheduler` and `getmail_nodelete`.

## start_email_scheduler Command

**Purpose**: Automatically fetch emails at regular intervals using APScheduler.

### Basic Syntax
```bash
python manage.py start_email_scheduler [options]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--interval` | Integer | 60 | Seconds between email fetches |
| `--no-verbose` | Flag | False | Disable verbose output |

### What It Does
- Runs an immediate email fetch when started
- Schedules recurring fetches at specified intervals
- Uses `UnreadOnlyNoMarkMailbox` (processes unread emails and keeps them unread)
- Handles shutdown signals gracefully (Ctrl+C)
- Logs all activities to `logs/scheduler.log`

### Examples

**Basic usage (60-second intervals)**:
```bash
python manage.py start_email_scheduler
```

**Custom interval (30 seconds)**:
```bash
python manage.py start_email_scheduler --interval 30
```

**Silent mode (no verbose output)**:
```bash
python manage.py start_email_scheduler --no-verbose
```

**Custom interval with silent mode**:
```bash
python manage.py start_email_scheduler --interval 120 --no-verbose
```

### Use Cases
- **Production automation**: Continuous email processing
- **Development testing**: Regular email monitoring
- **Background service**: Run as a system service

---

## getmail_nodelete Command

**Purpose**: Manually fetch unread emails without modifying them on the server.

### Basic Syntax
```bash
python manage.py getmail_nodelete [mailbox_names] [options]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mailbox_names` | List | All active | Specific mailbox names to process |
| `--verbose` | Flag | False | Enable detailed output |

### Email Processing Behavior

The command uses **UnreadOnlyNoMarkMailbox** which:
- **Processes**: Only unread emails in mailbox
- **Server action**: No changes (emails remain unread)
- **Database**: Saves only new emails (prevents duplicates using Message-ID)
- **Best for**: Non-destructive monitoring, preserving email status

### Examples

#### Basic Usage

**Process all mailboxes**:
```bash
python manage.py getmail_nodelete
```

**Process with verbose output**:
```bash
python manage.py getmail_nodelete --verbose
```

#### Specific Mailboxes

**Process specific mailboxes**:
```bash
python manage.py getmail_nodelete inbox support
```

**Process specific mailboxes with verbose output**:
```bash
python manage.py getmail_nodelete inbox support --verbose
```

### Use Cases

#### Development & Testing
```bash
# Safe testing - no changes to server
python manage.py getmail_nodelete --verbose
```

#### Production Monitoring
```bash
# Monitor unread emails without changing status
python manage.py getmail_nodelete --verbose
```

#### Specific Mailbox Processing
```bash
# Process only important mailboxes
python manage.py getmail_nodelete inbox alerts --verbose
```

---

## Docker Usage

### Scheduler in Docker
```bash
# View scheduler logs
docker-compose logs -f scheduler

# Restart scheduler
docker-compose restart scheduler

# Custom interval
docker-compose exec scheduler python manage.py start_email_scheduler --interval 30
```

### Manual Commands in Docker
```bash
# Process emails manually
docker-compose exec app python manage.py getmail_nodelete --verbose

# Process specific mailboxes
docker-compose exec app python manage.py getmail_nodelete inbox --verbose
```

---

## Quick Reference

### Common Scenarios

| Scenario | Command |
|----------|---------|
| Start automated processing | `python manage.py start_email_scheduler` |
| Test email fetching | `python manage.py getmail_nodelete --verbose` |
| Process specific mailboxes | `python manage.py getmail_nodelete inbox support --verbose` |
| Custom scheduler interval | `python manage.py start_email_scheduler --interval 30` |

### Parameter Combinations

| Parameters | Result |
|------------|--------|
| No parameters | Process all mailboxes, basic output |
| `--verbose` | Same as above but with detailed output |
| `mailbox1 mailbox2` | Process specific mailboxes, basic output |
| `mailbox1 mailbox2 --verbose` | Process specific mailboxes, detailed output |

---

## Best Practices

1. **Start with testing**: Use `--verbose` for initial setup to see what's happening
2. **Use verbose output**: Always add `--verbose` in production for monitoring
3. **Monitor specific mailboxes**: Process only the mailboxes you need to reduce load
4. **Monitor logs**: Check `logs/` directory for detailed information
5. **Test before automation**: Run manual commands before starting scheduler

## Key Features

- **Non-destructive**: Emails remain unchanged on the server
- **Unread-only**: Only processes emails that haven't been read
- **Duplicate prevention**: Built-in Message-ID checking prevents reprocessing
- **Flexible scheduling**: Configurable intervals for automated processing
- **Comprehensive logging**: Detailed logs for monitoring and debugging
