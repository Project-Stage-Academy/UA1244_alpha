import logging
from rest_framework.response import Response
from rest_framework import status


logger = logging.getLogger('django')

def get_success_response(message, data=None, status_code=status.HTTP_200_OK):
    """Utility function to standardize success responses."""
    response = Response({'message': message, 'data': data}, status=status_code)
    logger.info(f'Success response: {message}')
    return response


def handle_object_not_found(exception):
    """Utility function to handle not found responses."""
    response = Response({'message': 'Startup profile not found'}, status=status.HTTP_404_NOT_FOUND)
    logger.error(f'Object not found: {exception}')
    return response
