#!/usr/bin/env bash
set -euo pipefail

printf "api" >> /tmp/container-role

cd /app

echo "running collectstatic..."
python manage.py collectstatic --noinput

echo "starting server..."
if [[ "${DJANGO_DEBUG,,}" == "true" ]]; then
  echo "waiting for debugger..."
  mprof run --multiprocess python -m debugpy --wait-for-client --listen 0.0.0.0:9876 manage.py runserver_plus 0.0.0.0:9000
else
  mprof run --multiprocess python manage.py runserver 0.0.0.0:9000
fi
