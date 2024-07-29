from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Transaction


@registry.register_document
class TransactionDocument(Document):
    class Index:
        name = 'transactions'

    class Django:
        model = Transaction
        fields = [
            'amount',
            'date',
        ]
