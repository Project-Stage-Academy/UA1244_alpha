from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .models import User


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = self.get_token(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email,
        }, status=status.HTTP_200_OK)
