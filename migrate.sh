#!/usr/bin/env bash
# exit on error
set -o errexit

python3 manage.py makemigrations && python3 manage.py migrate