from rest_framework.response import Response
from rest_framework import status


def get_success_response(message, data=None, status_code=status.HTTP_200_OK):
    """Utility function to standardize success responses."""
    return Response({'message': message, 'data': data}, status=status_code)


def handle_object_not_found(exception):
    """Utility function to handle not found responses."""
    return Response({'message': 'Startup profile not found'}, status=status.HTTP_404_NOT_FOUND)
