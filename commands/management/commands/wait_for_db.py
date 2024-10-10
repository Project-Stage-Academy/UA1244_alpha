import time
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

from psycopg2 import OperationalError as psycopg2Error


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Waiting for database to be available...'))
        db_up = False
        wait_time = 1
        max_wait_time = 30

        while not db_up:
            try:
                connection = connections['default']
                connection.cursor().execute('SELECT 1')
                db_up = True
            except (OperationalError, psycopg2Error):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f'[{now}] Database not available, waiting {wait_time} seconds...')
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, max_wait_time)

        self.stdout.write(self.style.SUCCESS('Database available!'))
