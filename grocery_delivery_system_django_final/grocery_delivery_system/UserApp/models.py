from django.db import models
from django.conf import settings
from ProductsApp.models import Product
from StoreApp.models import Store 

# Create your models here.

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_cost(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Cart (User: {self.user.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product') 

    @property
    def total_price(self):
        return self.quantity * self.product.product_price

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"
    



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"



class StoreOrder(models.Model):
    order = models.ForeignKey(Order, related_name='store_orders', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    store_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered')
    ], default='pending')

    def __str__(self):
        return f"StoreOrder #{self.id} from {self.store.store_name} (Order #{self.order.id})"



class OrderItem(models.Model):
    store_order = models.ForeignKey(StoreOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for StoreOrder #{self.store_order.id}"
