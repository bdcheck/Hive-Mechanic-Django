import sys, os

INTERP = '/var/www/django/stokes/venv/bin/python'

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

import stokes.wsgi
application = stokes.wsgi.application
