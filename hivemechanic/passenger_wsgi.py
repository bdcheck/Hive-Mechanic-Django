import sys, os

INTERP = '/var/www/django/dev.hivemechanic.org/venv/bin/python'

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv) # nosec

sys.path.append(os.getcwd())

import hivemechanic.wsgi
application = hivemechanic.wsgi.application
