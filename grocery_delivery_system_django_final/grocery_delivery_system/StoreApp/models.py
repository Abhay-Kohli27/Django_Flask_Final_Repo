from django.db import models
from django.conf import settings
# from ProductsApp.models import Product

# Create your models here.
class Store(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(unique=True, max_length=20)
    store_category = models.CharField(max_length=20)
    store_description = models.TextField(max_length=200)
    store_logo = models.ImageField(upload_to="store_logo/",null=True)
    store_legal_business_name = models.CharField(max_length=40)
    tax_number = models.CharField(max_length=20)
    owner_name = models.CharField(max_length=20)
    business_email = models.EmailField(unique=True)
    store_address = models.TextField()
    business_documentation = models.ImageField(upload_to="store_documentation/", null=True)
    is_approved = models.BooleanField(null=False)
    opening_time = models.TimeField(null=True)
    closing_time = models.TimeField(null=True)

    def __str__(self):
        return self.store_name