# tests/test_views.py
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from customers.models import Customer
from transactions.models import Transaction
from loyalty_points.models import LoyaltyPoint


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer():
    return Customer.objects.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="09123456789"
    )


@pytest.mark.django_db
def test_customer_list_create_view(api_client):
    url = reverse('customer-list-create')
    response = api_client.get(url)
    assert response.status_code == 200

    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone_number": "09123456788"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_customer_detail_view(api_client, customer):
    url = reverse('customer-detail', args=[customer.pk])
    response = api_client.get(url)
    assert response.status_code == 200

    data = {
        "first_name": "Johnny",
        "last_name": "Doe",
        "email": "johnny.doe@example.com",
        "phone_number": "09123456787"
    }
    response = api_client.put(url, data, format='json')
    assert response.status_code == 200
    customer.refresh_from_db()
    assert customer.first_name == "Johnny"

    response = api_client.delete(url)
    assert response.status_code == 204
    assert Customer.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_for_customer(api_client, customer):
    url = reverse('customer-create-transaction', args=[customer.pk])
    data = {
        "amount": 100,
        "customer": str(customer.pk)
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert Transaction.objects.count() == 1
    assert LoyaltyPoint.objects.get(customer=customer).points == 1
