from django.core.management.base import BaseCommand

from deploy_tools.deployment import Deployment

from fabric.api import execute
from fabric.state import connections


class Command(BaseCommand):
    help = "deploy to staging or live PythonAnywhere servers"

    def add_arguments(self, parser):
        parser.add_argument(
            '--staging', dest='staging', action='store_true'
        )
        parser.add_argument(
            '--live', dest='staging', action='store_false'
        )

        parser.add_argument(
            '--initial', 
            action='store_true', 
            dest='initial', 
            default=False,
            help='Runs create_update_wsgi function'
        )

    def handle(self, *args, **options):
        deployment = Deployment(options['staging'])
        deployment.deploy(options['initial'], options['staging'])

        for key in connections.keys():
            connections[key].close()
            del connections[key]