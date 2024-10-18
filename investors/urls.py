from django.contrib import admin
from django.urls import path

from .views import (
    InvestorProfileViewById
)

urlpatterns = [
    path('investor-profile/<int:pk>/', InvestorProfileViewById.as_view(), name='investor-profile-by-id'),
]
