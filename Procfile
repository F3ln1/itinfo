web: python manage.py collectstatic --noinput --clear && python manage.py migrate --noinput && gunicorn itinfo.wsgi --bind 0.0.0.0:$PORT --workers 3
release: python manage.py migrate --noinput