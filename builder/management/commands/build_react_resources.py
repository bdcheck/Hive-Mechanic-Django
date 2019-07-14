# pylint: disable=no-member

import os
import shutil
import subprocess

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **cmd_options): # pylint: disable=unused-argument
        path = os.path.abspath(__file__)
        path = os.path.abspath(os.path.join(path, os.pardir))
        path = os.path.abspath(os.path.join(path, os.pardir))

        app_path = os.path.abspath(os.path.join(path, os.pardir))

        static_path = os.path.abspath(os.path.join(app_path, 'static'))
        static_path = os.path.abspath(os.path.join(static_path, 'builder-react'))

        react_path = os.path.abspath(os.path.join(app_path, 'react-source'))

        build_path = os.path.abspath(os.path.join(react_path, 'build'))

        subprocess.check_call('npm --prefix ' + str(react_path) + ' run build', shell=True)

        shutil.rmtree(static_path, ignore_errors=True)
        shutil.move(build_path, static_path)

        call_command('collectstatic', '--noinput')
