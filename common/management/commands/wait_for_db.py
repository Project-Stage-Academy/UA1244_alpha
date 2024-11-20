import logging
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from psycopg2 import OperationalError as psycopg2Error


logger = logging.getLogger('django')


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.debug('Starting command handling')
        self.stdout.write(self.style.NOTICE('Waiting for database to be available...'))
        logger.info('Waiting for database availability...')
        db_up = False
        wait_time = 1
        max_wait_time = 30

        while not db_up:
            try:
                connection = connections['default']
                connection.cursor().execute('SELECT 1')
                db_up = True

            except (OperationalError, psycopg2Error) as e:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f'[{now}] Database not available, waiting {wait_time} seconds...')
                logger.warning(f'Database not available, waiting {wait_time} seconds...')
                logger.error(f'Error accessing the database: {str(e)}')
                if wait_time >= max_wait_time:
                    logger.critical('Critical error: database has been unavailable for too long!')
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, max_wait_time)

        self.stdout.write(self.style.SUCCESS('Database available!'))
        logger.info('Database is now available!')
        logger.debug('Ending command handling')
