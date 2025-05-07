from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, StoreOrder

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1  # Add this line to show one empty row by default when editing a Cart

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'total_cost')
    search_fields = ('user__username',)
    inlines = [CartItemInline]  # This will allow editing of CartItems directly within the Cart form

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'created_at', 'updated_at', 'total_price')
    search_fields = ('cart__user__username', 'product__product_name')
    list_filter = ('cart', 'product')  # Add filters for easier searching and filtering by Cart or Product

# Register the models with the admin site
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

class StoreOrderInline(admin.StackedInline):
    model = StoreOrder
    extra = 0
    readonly_fields = ('store', 'store_total', 'status')
    show_change_link = True

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    inlines = [StoreOrderInline]

class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'store', 'store_total', 'status')
    list_filter = ('status', 'store')
    search_fields = ('store__store_name', 'order__user__username')
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_order', 'product', 'quantity', 'price')
    search_fields = ('product__product_name',)
    list_filter = ('store_order__store',)

# Register models with the admin site
admin.site.register(Order, OrderAdmin)
admin.site.register(StoreOrder, StoreOrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)