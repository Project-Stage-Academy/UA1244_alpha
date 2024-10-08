from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from django.contrib.auth.models import User as AuthUser


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = self.get_user(request.data)
            if user is not None:
                response.data.update({
                    'user_id': user.id,
                    'email': user.email,
                })
        return response

    def get_user(self, data):
        email = data.get('email')
        username = data.get('username')

        try:
            if email:
                return AuthUser.objects.get(email=email)
            elif username:
                return AuthUser.objects.get(username=username)
        except User.DoesNotExist:
            return None

