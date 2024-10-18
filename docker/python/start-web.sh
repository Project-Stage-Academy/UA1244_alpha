#!/bin/bash

set -euo pipefail

# Wait for PostgreSQL
python manage.py wait_for_db

# Run migrations
python manage.py migrate

# Check environment and start the appropriate server
if [[ "$DJANGO_ENV" = "PRODUCTION" ]]; then
  gunicorn -b 0.0.0.0:8000 \
    --log-level ${DJANGO_LOG_LEVEL,,} \
    --workers $(echo "$WEB_CONCURRENCY" | sed 's/[^0-9]//g') \
    --access-logfile - forum.wsgi:application
else
  # Initialize the admin (don't use it yet because the User model hasn't been created)
  # python manage.py initadmin
  python manage.py runserver 0.0.0.0:8000
fi
