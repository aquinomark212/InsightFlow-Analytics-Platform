#!/bin/bash

python manage.py migrate

python manage.py rqworker events cache analytics notifications &

daphne -b 0.0.0.0 -p 8000 config.asgi:application