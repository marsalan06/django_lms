#!/bin/sh

# Apply database migrations
python manage.py migrate
# Start the original command
exec "$@"