from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    CustomTokenObtainPairView, UserProfileView,
    CustomUserViewSet, LogoutView
)

router = DefaultRouter()
router.register(r'auth/users', CustomUserViewSet, basename='customuser')

urlpatterns = [
    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='token-create'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('auth/users/me/', UserProfileView.as_view(), name='user-profile'),
    path('auth/logout/', LogoutView.as_view(), name='logout-user'),

    path('auth/users/reset_password/', CustomUserViewSet.as_view({'post': 'reset_password'}), name='reset-password'),
    path('auth/users/get_roles/', CustomUserViewSet.as_view({'get': 'get_roles'}), name='get-roles'),
    path('auth/users/get_active_role/', CustomUserViewSet.as_view({'get': 'get_active_role'}), name='get-active-role'),
    path('auth/users/set_active_role/', CustomUserViewSet.as_view({'post': 'set_active_role'}), name='set-active-role'),
    path('auth/users/add_role/', CustomUserViewSet.as_view({'post': 'add_role'}), name='add-role'),
    path('auth/users/remove_role/', CustomUserViewSet.as_view({'post': 'remove_role'}), name='remove-role'),
    path('auth/users/soft_delete/', CustomUserViewSet.as_view({'post': 'soft_delete'}), name='soft-delete'),
    path('auth/users/reactivate/', CustomUserViewSet.as_view({'post': 'reactivate'}), name='reactivate'),
] + router.urls
