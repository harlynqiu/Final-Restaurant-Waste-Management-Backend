from django.urls import path
from .views import (
    SubscriptionPlanListView,
    MySubscriptionView,
    SubscribeToPlanView,
    CancelSubscriptionView,
    MyPaymentsView,
)

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='plan-list'),
    path('mine/', MySubscriptionView.as_view(), name='my-subscription'),
    path('subscribe/', SubscribeToPlanView.as_view(), name='subscribe-plan'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('payments/', MyPaymentsView.as_view(), name='my-payments'),
]
