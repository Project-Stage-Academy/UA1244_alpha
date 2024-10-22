from django.urls import path
from .views import InvestmentTrackingSaveView

urlpatterns = [
    path("startup/<int:startup_id>/save", InvestmentTrackingSaveView.as_view(), name = "save-followed-startups")

]