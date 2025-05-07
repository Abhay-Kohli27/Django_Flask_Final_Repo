from django.contrib import admin
from ProductsApp.models import Product, ProductImage, Review

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_id','product_name','product_price','product_category','product_quantity','product_description','store_id','created_at','updated_at','featured_product','stock_threshold']
    search_fields=['product_id','product_name']
    list_filter=['product_price','product_quantity','featured_product']

class ProductImageAdmin(admin.ModelAdmin):
    list_display=['product_id','image']
    search_fields=['product_id']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__product_name', 'comment')

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Review, ReviewAdmin)