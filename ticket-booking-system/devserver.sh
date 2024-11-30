#!/bin/sh
source .tbs-env/bin/activate
python manage.py runserver $PORT || {
  echo "Error: Failed to start Django development server"
  exit 1
}
