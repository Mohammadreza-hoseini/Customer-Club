from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Customer
from .serializers import CustomerSerializer
from transactions.serializers import TransactionSerializer
from django.db import transaction
from loyalty_points.models import LoyaltyPoint
from .documents import CustomerDocument
from rest_framework.views import APIView
from rest_framework import status
from elasticsearch_dsl import Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


@transaction.atomic
@api_view(['POST'])
def create_transaction_for_customer(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=404)

    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(customer=customer)

        # Update loyalty points
        points = 1  # Assume that each 1 transaction unit has 1 point

        # Check if a loyalty point record exists for the customer
        try:
            loyalty_point = LoyaltyPoint.objects.get(customer=customer)
            loyalty_point.points += 1
            loyalty_point.save()
        except LoyaltyPoint.DoesNotExist:
            LoyaltyPoint.objects.create(customer=customer, points=points)

        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


class CustomerSearchView(APIView):
    @method_decorator(cache_page(60 * 15))  # Caching is for 15 minutes
    def get(self, request):
        query = request.GET.get('query', '')
        if query:
            get_query = Q("wildcard", first_name=f"{query}*") | Q("wildcard", email=f"{query}*")
            search_query = CustomerDocument.search().query(get_query)
            serializer = CustomerSerializer(search_query.to_queryset(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            get_query = Q("match_all")
        search_query = CustomerDocument.search().query(get_query)
        serializer = CustomerSerializer(search_query.to_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
