# D1 Database Migration System

This document describes the migration system for the Trading Cloud Brain D1 (SQLite) database.

## Overview

The migration system provides a robust, production-ready solution for managing database schema changes in both development and production environments. It supports versioning, rollback capabilities, and proper tracking of applied migrations.

## Features

- **Version Control**: Semantic versioning with timestamp-based migration files
- **Tracking**: Automatic tracking of applied migrations in the database
- **Rollback**: Support for rolling back migrations (tracking removal)
- **Environment Support**: Separate configurations for development and production
- **Error Handling**: Comprehensive error handling and logging
- **Checksum Verification**: SHA256 checksums ensure migration integrity
- **Multi-statement Support**: Handles complex migrations with multiple SQL statements

## File Structure

```
trading-cloud-brain/
├── migrations/
│   └── 0001_initial_schema.sql    # Initial database schema
├── apply_migrations.py             # Migration management script
├── requirements.txt                # Python dependencies
└── MIGRATION_SYSTEM.md           # This documentation
```

## Migration Files

Migration files follow the naming convention: `{version}_{description}.sql`

- **Version**: Sequential number (e.g., 0001, 0002)
- **Description**: Brief description of the migration purpose
- **Example**: `0002_add_user_indexes.sql`

### Migration File Format

Each migration file should include:

```sql
-- Migration number: 0002 ⏱️ 2025-12-14T05:30:00Z
-- Brief description of migration purpose
-- Environment: D1 (Cloudflare SQLite)

-- Your SQL statements here
CREATE TABLE IF NOT EXISTS example_table (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_example_name ON example_table(name);
```

## Usage

### Basic Commands

#### Initialize Migration System
```bash
python apply_migrations.py init --env dev
```

#### Check Migration Status
```bash
python apply_migrations.py status --env dev
```

#### Apply Pending Migrations
```bash
python apply_migrations.py apply --env dev
```

#### Rollback Migration
```bash
python apply_migrations.py rollback --version 0001_initial_schema --env dev
```

### Environment Configuration

#### Development
```bash
python apply_migrations.py status --env dev
```
- Uses local database file: `trading_brain.db`
- Default environment for local development

#### Production
```bash
python apply_migrations.py status --env production
```
- Uses database path from `D1_DATABASE_PATH` environment variable
- Requires proper environment configuration

### Advanced Options

#### Custom Database Path
```bash
python apply_migrations.py status --db-path /path/to/custom.db
```

#### Custom Migrations Directory
```bash
python apply_migrations.py status --migrations-dir /path/to/migrations
```

#### Verbose Logging
```bash
python apply_migrations.py apply --env dev --verbose
```

## Database Schema

### Core Tables

#### trades
The core trading ledger storing all trade executions.

#### signals
AI decision log storing all generated trading signals.

#### signal_events
Detailed signal events with market context and component scores.

#### signal_outcomes
Performance tracking for signal accuracy over time.

#### learning_metrics
Aggregated performance metrics for analysis.

#### weight_history
Evolution log for weight optimization tracking.

#### news
Market news articles with sentiment analysis.

#### briefings
Daily AI-generated market briefings.

#### user_connections
OAuth connections for payment providers.

#### trade_orders
Trade orders executed through the platform.

#### system_alerts
System monitoring and alerting.

#### system_monitoring
Performance metrics and observability data.

#### telegram_reports
Audit trail for Telegram reports.

### Migration Tracking

#### schema_migrations
Tracks applied migrations with checksums for integrity verification.

## Migration Workflow

### Creating New Migrations

1. Create new migration file in `migrations/` directory
2. Follow naming convention: `0002_description.sql`
3. Add proper header with timestamp and description
4. Write SQL statements with proper error handling
5. Test migration in development environment

### Testing Process

1. Initialize migration system: `python apply_migrations.py init --env dev`
2. Check status: `python apply_migrations.py status --env dev`
3. Apply migration: `python apply_migrations.py apply --env dev`
4. Verify database schema changes
5. Test rollback: `python apply_migrations.py rollback --version <version> --env dev`

### Production Deployment

1. Ensure all migrations tested in development
2. Set `D1_DATABASE_PATH` environment variable
3. Run status check: `python apply_migrations.py status --env production`
4. Apply migrations: `python apply_migrations.py apply --env production`
5. Verify successful deployment

## Best Practices

### Migration Files

- **Atomic Operations**: Each migration should be atomic and reversible
- **Idempotent**: Use `IF NOT EXISTS` clauses for safe re-runs
- **Documentation**: Include clear comments explaining changes
- **Performance**: Add appropriate indexes for new tables
- **Testing**: Test migrations on sample data before production

### Error Handling

- **Transactions**: Use transactions for complex migrations
- **Rollback Plans**: Always have rollback strategies
- **Logging**: Enable verbose logging for debugging
- **Validation**: Verify data integrity after migrations

### Security

- **Environment Variables**: Never hard-code database credentials
- **Access Control**: Limit database access during migrations
- **Backups**: Create database backups before major migrations
- **Audit Trail**: Maintain migration history for compliance

## Troubleshooting

### Common Issues

#### Migration Already Applied
```
Error: Migration version already exists
```
Solution: Check status and verify migration state

#### SQL Syntax Error
```
Error: Failed to apply migration <version>: SQL syntax error
```
Solution: Review SQL syntax and test in isolation

#### Database Connection Error
```
Error: Failed to connect to database
```
Solution: Verify database path and permissions

#### Rollback Failure
```
Error: Migration <version> not found in applied migrations
```
Solution: Check current migration status

### Debug Mode

Enable verbose logging for detailed debugging:
```bash
python apply_migrations.py apply --env dev --verbose
```

### Manual Recovery

If migration system becomes corrupted:

1. Check `schema_migrations` table directly
2. Manually remove problematic migration records
3. Re-initialize with `python apply_migrations.py init`
4. Apply migrations individually

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Apply Database Migrations
  run: |
    python apply_migrations.py apply --env production
  env:
    D1_DATABASE_PATH: ${{ secrets.D1_DATABASE_PATH }}
```

### Environment Variables

- `D1_DATABASE_PATH`: Path to production database file
- `PYTHONPATH`: Ensure Python can find migration script

## Dependencies

### Python Requirements
```
fastapi
uvar
sqlite3
argparse
hashlib
```

### System Requirements
- Python 3.7+
- SQLite 3.x
- File system permissions for database directory

## Performance Considerations

### Migration Optimization
- **Batch Operations**: Group related changes in single migrations
- **Index Strategy**: Add indexes after data migration
- **Transaction Size**: Keep transactions manageable
- **Lock Duration**: Minimize database lock time

### Database Performance
- **Index Maintenance**: Regularly analyze and optimize indexes
- **Query Planning**: Use EXPLAIN QUERY PLAN for complex queries
- **Connection Pooling**: Reuse connections for multiple operations

## Security Considerations

### Access Control
- **Principle of Least Privilege**: Limit database user permissions
- **Connection Security**: Use secure connection methods
- **Audit Logging**: Log all migration activities

### Data Protection
- **Encryption**: Encrypt sensitive data at rest
- **Backup Strategy**: Regular, automated backups
- **Recovery Planning**: Document recovery procedures

## Monitoring and Alerting

### Migration Metrics
- **Migration Duration**: Track time for each migration
- **Success Rate**: Monitor migration success/failure rates
- **Rollback Frequency**: Track rollback usage patterns

### Database Health
- **Connection Count**: Monitor database connections
- **Query Performance**: Track slow queries
- **Storage Usage**: Monitor database size growth

## Future Enhancements

### Planned Features
- **Automatic Rollback**: Generate rollback SQL automatically
- **Migration Dependencies**: Handle complex migration dependencies
- **Parallel Execution**: Support for parallel safe migrations
- **Web Interface**: Browser-based migration management

### Integration Opportunities
- **Cloudflare Workers**: Direct D1 API integration
- **GraphQL Schema**: Auto-generate GraphQL schemas
- **API Documentation**: Generate API docs from schema changes

## Support

For issues or questions about the migration system:

1. Check this documentation first
2. Review error logs with verbose mode
3. Test in development environment
4. Check GitHub issues for known problems
5. Contact development team for assistance

## Version History

- **v1.0**: Initial migration system implementation
- **v1.1**: Added checksum verification and rollback support
- **v1.2**: Enhanced error handling and logging
- **v1.3**: Added production environment support

---

*Last Updated: 2025-12-14*
*Version: 1.0*