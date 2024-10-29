#!/usr/bin/.env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging


logger = logging.getLogger(__name__)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')
    logging.info("Running administrative tasks...")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logging.error("Failed to import Django. Check your installation.", exc_info=True)
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    logger.info("Executing command: %s", " ".join(sys.argv))
    execute_from_command_line(sys.argv)
    logging.info("Completing administrative tasks.")


if __name__ == '__main__':
    main()
