from django.urls import path
from .views import CustomerListCreateView, CustomerDetailView, create_transaction_for_customer, CustomerSearchView

urlpatterns = [
    path('', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('<uuid:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('<uuid:pk>/transactions/', create_transaction_for_customer, name='customer-create-transaction'),
    path('search/', CustomerSearchView.as_view(), name='customer-search'),
]
