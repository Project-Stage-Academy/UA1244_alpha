from django.shortcuts import render
from rest_framework import generics, status

from .models import InvestorProfile


class InvestorProfileViewById(generics.RetrieveAPIView):
    pass
