import pytest
from rest_framework import status
from rest_framework.test import APIClient
from transactions.models import Transaction
from customers.models import Customer
from decimal import Decimal
from django.utils import timezone


@pytest.mark.django_db
def test_search_by_amount():
    client = APIClient()
    customer = Customer.objects.create(first_name="John", last_name="Doe", email="john@example.com",
                                       phone_number="09379921725")
    Transaction.objects.create(
        customer=customer,
        amount=Decimal('100.00'),
        date=timezone.now()
    )

    response = client.get('/api/transactions/search/', {'query': '100.00'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['amount'] == '100.00'


@pytest.mark.django_db
def test_search_by_date():
    client = APIClient()
    customer = Customer.objects.create(first_name="John", email="john@example.com")
    transaction = Transaction.objects.create(
        customer=customer,
        amount=Decimal('100.00'),
        date=timezone.now()
    )
    date_str = transaction.date.strftime("%Y-%m-%d")

    response = client.get('/api/transactions/search/', {'query': date_str})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['amount'] == '100.00'
