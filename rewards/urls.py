from django.urls import path
from .views import (
    RewardPointView,
    RewardTransactionListView,
    VoucherListView,
    RedeemVoucherView,
    RewardRedemptionListView,
    MyRewardsListView
)

urlpatterns = [
    path('points/', RewardPointView.as_view(), name='reward-points'),
    path('transactions/', RewardTransactionListView.as_view(), name='reward-transactions'),
    path('vouchers/', VoucherListView.as_view(), name='voucher-list'),
    path('redeem/', RedeemVoucherView.as_view(), name='redeem-voucher'),
    path('redemptions/', RewardRedemptionListView.as_view(), name='redemption-list'),
    path('my_rewards/', MyRewardsListView.as_view(), name='my_rewards')
]
