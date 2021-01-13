#!/bin/bash
gunicorn --bind 0:8002 app.main:app --reload -w ${GUNICORN_WORKERS:=1}