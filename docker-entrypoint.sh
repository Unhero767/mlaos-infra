#!/bin/bash
# Docker entrypoint script for MLAOS API
# Handles database initialization and migrations before starting the API

set -e

# Wait for database to be ready
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for PostgreSQL to be ready..."
  
  until python -c "
import psycopg2
import sys
from urllib.parse import urlparse

db_url = '$DATABASE_URL'
try:
    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/')
    )
    conn.close()
    print('Database is ready!')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done
  
  echo "PostgreSQL is up - running migrations"
  
  # Run SQL migrations
  python << 'EOF'
import psycopg2
import os
from urllib.parse import urlparse

db_url = os.environ.get('DATABASE_URL')
if db_url:
    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/')
    )
    
    # Run migrations from sql directory
    sql_dir = '/app/sql'
    for sql_file in sorted(os.listdir(sql_dir)):
        if sql_file.endswith('.sql'):
            file_path = os.path.join(sql_dir, sql_file)
            with open(file_path, 'r') as f:
                sql_content = f.read()
            
            with conn.cursor() as cur:
                cur.execute(sql_content)
            conn.commit()
            print(f"Executed migration: {sql_file}")
    
    conn.close()
    print("All migrations completed successfully")
EOF
fi

# Execute the main command
exec "$@"
