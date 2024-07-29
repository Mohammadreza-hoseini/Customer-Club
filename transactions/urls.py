from django.urls import path
from .views import TransactionListView, TransactionDetailView, search_transactions

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<uuid:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('search/', search_transactions, name='transaction-search'),
]
