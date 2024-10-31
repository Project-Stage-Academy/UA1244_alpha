import logging
from django.apps import AppConfig


logger = logging.getLogger('django')


class InvestorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'investors'

    def ready(self):
        logger.info('Initializing Investors app and importing signals.')
        try:
            import investors.signals  # noqa
            logger.info('Successfully imported signals for Investors app.')
        except Exception as e:
            logger.error(f'Failed to import signals for Investors app. Error: {e}')
            raise
