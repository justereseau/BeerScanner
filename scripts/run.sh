#!/bin/bash
. ./venv/bin/activate
uwsgi --socket localhost:8000 --chdir /opt/BeerScanner/app --wsgi-file AppManager/wsgi.py --master --processes 2 --threads 1 --uid pi
