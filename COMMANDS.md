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
- Uses `unreadonlynomark` transport by default (processes unread emails and keeps them unread)
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

**Purpose**: Manually fetch emails using different transport types without deleting from server.

### Basic Syntax
```bash
python manage.py getmail_nodelete [mailbox_names] [options]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mailbox_names` | List | All active | Specific mailbox names to process |
| `--transport-type` | Choice | nodelete | Transport type to use |
| `--verbose` | Flag | False | Enable detailed output |

### Transport Types

| Type | Behavior | Use Case |
|------|----------|----------|
| `nodelete` | Process all emails, keep unchanged | Testing, development, data migration |
| `markread` | Process all emails, mark as read | Production tracking |
| `unreadonly` | Process unread emails, mark as read | Regular automation, performance |
| `unreadonlynomark` | Process unread emails, keep unread | Special cases, preserve status |

### Transport Type Details

#### 1. nodelete (Default)
- **Processes**: All emails in mailbox
- **Server action**: No changes (emails remain as-is)
- **Database**: Saves all processed emails
- **Best for**: Testing, development, one-time imports

#### 2. markread
- **Processes**: All emails in mailbox
- **Server action**: Marks emails as read
- **Database**: Saves all processed emails
- **Best for**: Production environments, tracking processed emails

#### 3. unreadonly
- **Processes**: Only unread emails
- **Server action**: Marks processed emails as read
- **Database**: Saves only new emails
- **Best for**: Regular automation, avoiding reprocessing

#### 4. unreadonlynomark
- **Processes**: Only unread emails
- **Server action**: Keeps emails unread
- **Database**: Saves only new emails (prevents duplicates)
- **Best for**: Special monitoring, preserving email status

### Examples

#### Basic Usage

**Process all mailboxes (no deletion)**:
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

**Process specific mailboxes with mark-as-read**:
```bash
python manage.py getmail_nodelete inbox support --transport-type markread
```

#### Transport Type Examples

**Mark emails as read (production)**:
```bash
python manage.py getmail_nodelete --transport-type markread --verbose
```

**Process only unread emails**:
```bash
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

**Process unread emails without marking as read**:
```bash
python manage.py getmail_nodelete --transport-type unreadonlynomark --verbose
```

#### Combined Parameters

**Specific mailboxes + transport + verbose**:
```bash
python manage.py getmail_nodelete inbox support --transport-type unreadonly --verbose
```

**All mailboxes + special transport + verbose**:
```bash
python manage.py getmail_nodelete --transport-type unreadonlynomark --verbose
```

### Use Cases by Transport Type

#### Development & Testing
```bash
# Safe testing - no changes to server
python manage.py getmail_nodelete --transport-type nodelete --verbose
```

#### Production Deployment
```bash
# Track processed emails
python manage.py getmail_nodelete --transport-type markread --verbose
```

#### Regular Automation
```bash
# Efficient processing, avoid duplicates
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

#### Special Monitoring
```bash
# Monitor without changing email status
python manage.py getmail_nodelete --transport-type unreadonlynomark --verbose
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

# Use specific transport
docker-compose exec app python manage.py getmail_nodelete --transport-type unreadonlynomark --verbose

# Process specific mailboxes
docker-compose exec app python manage.py getmail_nodelete inbox --transport-type markread --verbose
```

---

## Quick Reference

### Common Scenarios

| Scenario | Command |
|----------|---------|
| Start automated processing | `python manage.py start_email_scheduler` |
| Test email fetching | `python manage.py getmail_nodelete --verbose` |
| Production processing | `python manage.py getmail_nodelete --transport-type markread --verbose` |
| Process only new emails | `python manage.py getmail_nodelete --transport-type unreadonly --verbose` |
| Monitor without changes | `python manage.py getmail_nodelete --transport-type unreadonlynomark --verbose` |
| Custom scheduler interval | `python manage.py start_email_scheduler --interval 30` |

### Parameter Combinations

| Parameters | Result |
|------------|--------|
| No parameters | Process all mailboxes, no deletion, basic output |
| `--verbose` | Same as above but with detailed output |
| `--transport-type markread` | Process all emails, mark as read |
| `--transport-type unreadonly --verbose` | Process unread emails, mark as read, detailed output |
| `mailbox1 mailbox2 --verbose` | Process specific mailboxes, detailed output |
| `--transport-type unreadonlynomark --verbose` | Process unread emails, keep unread, detailed output |

---

## Best Practices

1. **Start with testing**: Use `nodelete` transport for initial setup
2. **Use verbose output**: Always add `--verbose` in production for monitoring
3. **Choose appropriate transport**: 
   - `markread` for production tracking
   - `unreadonly` for regular automation
   - `unreadonlynomark` for special monitoring
4. **Monitor logs**: Check `logs/` directory for detailed information
5. **Test before automation**: Run manual commands before starting scheduler
