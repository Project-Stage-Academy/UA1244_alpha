import logging
from django.core.management.base import BaseCommand
from django.core.cache import cache

logger = logging.getLogger('django')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        logger.debug('Starting cache clearing command')
        cache.clear()
        logger.info('Cache has been cleared!')
        self.stdout.write(self.style.SUCCESS('Cache has been cleared!'))
        logger.debug('Ending cache clearing command')