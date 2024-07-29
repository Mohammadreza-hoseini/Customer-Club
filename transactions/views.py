import datetime

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transaction
from .serializers import TransactionSerializer
from elasticsearch_dsl import Q
from .documents import TransactionDocument
from rest_framework import status
from django.views.decorators.cache import cache_page


class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionDetailView(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


def parse_datetime(query):
    """Convert string to datetime object based on different formats"""
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.datetime.strptime(query, fmt)
        except ValueError:
            continue
    raise ValueError("Invalid date or time format")


def build_date_range(query_date, fmt):
    """Build time range based on date"""
    if fmt == "%Y-%m-%d":
        start = datetime.datetime.combine(query_date, datetime.time.min)
        end = datetime.datetime.combine(query_date, datetime.time.max)
    elif fmt == "%Y-%m":
        start = datetime.datetime.combine(query_date, datetime.time.min)
        end = datetime.datetime.combine(
            (query_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1),
            datetime.time.min
        ) - datetime.timedelta(microseconds=1)
    elif fmt == "%Y":
        start = datetime.datetime.combine(query_date, datetime.time.min)
        end = datetime.datetime.combine(
            (query_date.replace(year=query_date.year + 1, month=1, day=1)),
            datetime.time.min
        ) - datetime.timedelta(microseconds=1)
    else:
        raise ValueError("The date format is invalid")

    return start, end


@api_view(['GET'])
@cache_page(60 * 15)
def search_transactions(request):
    query = request.GET.get('query', '')

    if query:
        try:
            query_datetime = parse_datetime(query)

            if query_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == query:
                # Detailed search by date and time
                q = Q("term", date=query_datetime)
            else:
                # Check the date format
                try:
                    fmt = "%Y-%m-%d" if len(query) == 10 else "%Y-%m" if len(query) == 7 else "%Y"
                    start, end = build_date_range(query_datetime, fmt)
                    q = Q("range", date={"gte": start, "lte": end})
                except ValueError:
                    # Search for amount
                    q = Q("multi_match", query=query, fields=['amount', 'date'])
        except ValueError:
            # Search for other values if the format is invalid
            q = Q("multi_match", query=query, fields=['amount', 'date'])
    else:
        # If query is empty, search all results
        q = Q("match_all")

    # Run a search
    transactions = TransactionDocument.search().query(q)
    serializer = TransactionSerializer(transactions.to_queryset(), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
