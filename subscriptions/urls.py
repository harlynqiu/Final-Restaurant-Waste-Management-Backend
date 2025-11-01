# subscriptions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("plans/", views.SubscriptionPlanListView.as_view(), name="subscription_plans"),
    path("mine/", views.MySubscriptionView.as_view(), name="my_subscription"),
    path("subscribe/", views.SubscribeToPlanView.as_view(), name="subscribe_to_plan"),
    path("cancel/", views.CancelSubscriptionView.as_view(), name="cancel_subscription"),
    path("payments/", views.MyPaymentsView.as_view(), name="my_payments"),
]
