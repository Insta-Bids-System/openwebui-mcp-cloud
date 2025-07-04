#!/bin/bash
# backup.sh - Daily backup script

# Configuration
BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Source environment variables
source /root/openwebui-mcp-cloud/.env.production

echo "Starting backup: $DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup workspace files
echo "Backing up workspace..."
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz /data/workspace

# Backup OpenWebUI data
echo "Backing up OpenWebUI data..."
docker exec open-webui tar -czf - /app/backend/data > $BACKUP_DIR/openwebui_$DATE.tar.gz

# Backup PostgreSQL if using local instance
if docker ps | grep -q postgres; then
    echo "Backing up PostgreSQL..."
    docker exec postgres pg_dumpall -U postgres > $BACKUP_DIR/postgres_$DATE.sql
fi

# Backup configurations
echo "Backing up configurations..."
tar -czf $BACKUP_DIR/configs_$DATE.tar.gz \
    /root/openwebui-mcp-cloud/.env.production \
    /root/openwebui-mcp-cloud/docker-compose.production.yml \
    /data/mcp-configs

# Upload to S3 if configured
if [ ! -z "$S3_BACKUP_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp $BACKUP_DIR/workspace_$DATE.tar.gz s3://$S3_BACKUP_BUCKET/
    aws s3 cp $BACKUP_DIR/openwebui_$DATE.tar.gz s3://$S3_BACKUP_BUCKET/
    aws s3 cp $BACKUP_DIR/configs_$DATE.tar.gz s3://$S3_BACKUP_BUCKET/
fi

# Clean old local backups
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete

# Log backup status
echo "Backup completed: $DATE" >> /var/log/backup.log