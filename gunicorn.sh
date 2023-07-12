#!/bin/sh
gunicorn "parsing_service:create_app()" -w "${GUNICORN_WORKERS:-2}" --timeout "${GUNICORN_WORKERS_TIMEOUT:-600}" -b 0.0.0.0:5000