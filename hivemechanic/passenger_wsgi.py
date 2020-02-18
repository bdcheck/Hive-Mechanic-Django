import os
import sys

install_dir = os.path.dirname(os.path.abspath(__file__))
install_dir = os.path.dirname(install_dir)
install_dir = os.path.dirname(install_dir)

INTERP = os.path.join(install_dir, 'venv/bin/python')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv) # nosec

sys.path.append(os.getcwd())

import hivemechanic.wsgi
application = hivemechanic.wsgi.application
