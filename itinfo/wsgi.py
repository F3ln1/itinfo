import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinfo.settings')

call_command('collectstatic', '--noinput', '--clear', stdout=open(os.devnull, 'w'))
call_command('migrate', '--noinput', stdout=open(os.devnull, 'w'))

application = get_wsgi_application()
