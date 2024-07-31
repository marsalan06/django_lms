#!/bin/sh

# Apply database migrations
python manage.py migrate --noinput

# Start the original command
exec "$@"