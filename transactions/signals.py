from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction
from .documents import TransactionDocument


@receiver(post_save, sender=Transaction)
def index_transaction(sender, instance, **kwargs):
    transaction_doc = TransactionDocument(
        meta={'id': instance.id},
        customer={
            'first_name': instance.customer.first_name,
            'last_name': instance.customer.last_name,
            'email': instance.customer.email,
            'phone_number': instance.customer.phone_number,
        },
        amount=instance.amount,
        date=instance.date,
    )
    transaction_doc.save()
