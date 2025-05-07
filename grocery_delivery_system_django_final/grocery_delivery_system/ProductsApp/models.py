from django.db import models
from StoreApp.models import Store
from django.conf import settings


# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=30)
    product_price = models.DecimalField(max_digits=10, decimal_places=4)
    product_category = models.CharField(max_length=20, null=False)
    product_quantity = models.IntegerField()
    product_description = models.TextField()
    stock_threshold = models.IntegerField(null=True)
    featured_product = models.BooleanField(null=True)
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        return f"Product name: {self.product_name}"


class ProductImage(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/",null=False, blank=False)



class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField() 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  


    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.rating}★)"