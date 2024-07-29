from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer
from .documents import CustomerDocument


@receiver(post_save, sender=Customer)
def index_customer(sender, instance, **kwargs):
    customer_doc = CustomerDocument(
        meta={'id': instance.id},
        first_name=instance.first_name,
        last_name=instance.last_name,
        email=instance.email,
        phone_number=instance.phone_number,
    )
    customer_doc.save()
