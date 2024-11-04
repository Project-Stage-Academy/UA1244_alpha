from django.urls import path
from .views import InvestmentTrackingSaveView

urlpatterns = [
    path("startup/<int:sender_id>/save/", InvestmentTrackingSaveView.as_view(), name="save-followed-startups"),
    # path("investor/saved-startups/", InvestmentTrackingListView.as_view(), name="list-saved-startups"),
    # path("startup/<int:sender_id>/unsave/", InvestmentTrackingUnsaveView.as_view(), name="unsave-followed-startups"),
]
