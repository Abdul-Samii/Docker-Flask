#!/bin/sh

echo '⏳ Waiting for PostgreSQL to be ready...'
until nc -z postgres 5432; do
  sleep 1
done
echo '✅ PostgreSQL is up - starting API...'
exec "$@"
