from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from djoser.views import UserViewSet
from users.views import CustomTokenObtainPairView, UserProfileView, CustomUserViewSet

urlpatterns = [
    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='token-create'),  # Login
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('auth/users/', UserViewSet.as_view({'post': 'create'}), name='user-create'),                   # create new user
    path('auth/users/me/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='current-user'),  # about current user
    path('auth/users/set_password/', UserViewSet.as_view({'post': 'set_password'}), name='set-password'),     # Change password
    path('auth/users/reset_password/', CustomUserViewSet.as_view({'post': 'reset_password'}), name='reset-password'),   # Password reset request
    path('auth/users/reset_password_confirm/', UserViewSet.as_view({'post': 'reset_password_confirm'}), name='reset-password-confirm'),  # Confirm password reset
    path('auth/users/activation/', UserViewSet.as_view({'post': 'activation'}), name='user-activation'),    # Account activation
    path('auth/users/resend_activation/', UserViewSet.as_view({'post': 'resend_activation'}), name='resend-activation'),  # Resending activation
    path('auth/users/profile/', UserProfileView.as_view(), name='user-profile'),
]
