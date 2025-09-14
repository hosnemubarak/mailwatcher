# MailWatcher Command Usage Guide

This document explains the use cases and practical applications of the `getmail_nodelete` management command with different options.

## Command Overview

The `getmail_nodelete` command provides flexible email processing with three main transport types that handle emails differently on the server.

## Command Examples and Use Cases

### 1. Process All Active Mailboxes Without Deleting

```bash
python manage.py getmail_nodelete
```

**Use Case**: **Bulk processing with preservation**

- **Scope**: Processes **all active mailboxes** in your Django application
- **Transport**: Uses the default `NoDeleteImapTransport` behavior
- **Server Impact**: **Preserves all emails** on the server - nothing gets deleted
- **Email Handling**: Fetches and processes all emails while keeping them intact

**Ideal for**:
- Initial setup and testing
- Data migration scenarios
- Backup and archival purposes
- When you want to keep all emails intact on the server
- Development environments where you don't want to lose emails

### 2. Process Specific Mailboxes with Mark-as-Read

```bash
python manage.py getmail_nodelete inbox support --transport-type markread
```

**Use Case**: **Selective processing with tracking**

- **Scope**: Processes **only specific mailboxes** (`inbox` and `support` in this example)
- **Transport**: Uses `MarkAsReadImapTransport` 
- **Server Impact**: **Marks emails as read** instead of deleting them using the `\Seen` flag
- **Email Handling**: **Tracks which emails have been processed** for future reference

**Ideal for**:
- Production environments where you want to avoid reprocessing
- Customer support workflows
- Audit trails and compliance requirements
- When you need to track processed vs unprocessed emails
- Selective processing of important mailboxes only

### 3. Process Only Unread Emails with Verbose Output

```bash
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

**Use Case**: **Efficient incremental processing**

- **Scope**: Processes **all active mailboxes**
- **Transport**: Uses `UnreadOnlyImapTransport`
- **Server Impact**: Only fetches **unread emails** and **marks them as read** after processing
- **Email Handling**: Avoids reprocessing already handled emails using `UNSEEN` search
- **Output**: **Verbose logging** provides detailed information for monitoring

**Ideal for**:
- Regular automated processing (cron jobs)
- Performance optimization with large mailboxes
- Avoiding duplicate processing
- Production monitoring and debugging
- Incremental email processing workflows

## Comparison Table

| Command | Scope | Email Selection | Server State After Processing | Performance | Best For |
|---------|-------|----------------|-------------------------------|-------------|----------|
| **Command 1** | All mailboxes | All emails | No changes (preserved) | Slower (processes all) | Initial setup, backup |
| **Command 2** | Specific mailboxes | All emails in selected boxes | Marked as read | Medium (selective scope) | Targeted processing |
| **Command 3** | All mailboxes | Unread emails only | Marked as read | Faster (unread only) | Regular automation |

## Transport Type Details

### NoDeleteImapTransport (Default)
- **Behavior**: Fetches and processes all emails without server modifications
- **Server State**: Emails remain unchanged
- **Use When**: You want to preserve original email state

### MarkAsReadImapTransport (`--transport-type markread`)
- **Behavior**: Processes emails and marks them with `\Seen` flag
- **Server State**: Emails marked as read
- **Use When**: You need to track processed emails

### UnreadOnlyImapTransport (`--transport-type unreadonly`)
- **Behavior**: Only fetches unread emails, then marks them as read
- **Server State**: Processed emails marked as read
- **Use When**: You want efficient incremental processing

## Workflow Recommendations

### Development/Testing
```bash
# Safe testing - preserves all emails
python manage.py getmail_nodelete --verbose
```

### Production Deployment
```bash
# Process specific critical mailboxes with tracking
python manage.py getmail_nodelete inbox support billing --transport-type markread --verbose
```

### Regular Automation
```bash
# Efficient daily processing - only new emails
python manage.py getmail_nodelete --transport-type unreadonly --verbose
```

## Additional Options

- **`--verbose`**: Enables detailed logging output for monitoring and debugging
- **Mailbox Names**: Specify one or more mailbox names to process only those mailboxes
- **`--transport-type`**: Choose between `nodelete` (default), `markread`, or `unreadonly`

## Best Practices

1. **Start with `nodelete`** for initial testing and setup
2. **Use `markread`** for production environments where you need tracking
3. **Use `unreadonly`** for regular automated processing to improve performance
4. **Always use `--verbose`** in production for proper monitoring
5. **Specify mailbox names** when you only need to process specific mailboxes
6. **Test thoroughly** in development before deploying to production

This flexible command structure allows you to adapt email processing to your specific workflow requirements while maintaining full control over server-side email management.
