from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem, StoreOrder
from ProductsApp.models import Product
from decimal import Decimal

@login_required
def view_cart(request):
    
    cart, new_cart = Cart.objects.get_or_create(user=request.user)
    
    cart_items = cart.items.all().select_related('product')

    cart = request.user.cart
    total_quantity = sum(item.quantity for item in cart.items.all())
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_quantity':total_quantity
    }
    return render(request, 'cart.html', context)



@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.product_name} added to your cart.')
    return redirect('home')



@login_required
def update_or_remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=request.user.cart)
    except CartItem.DoesNotExist:
        return redirect('view_cart')

    if request.method == 'POST':
        if 'update_item' in request.POST:
            try:
                quantity = int(request.POST.get('quantity'))
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
            except (ValueError, TypeError):
                pass  

        elif 'remove_item' in request.POST:
            cart_item.delete()

    return redirect('view_cart')



@login_required
def checkout(request):

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all().select_related('product')
        
        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect('view_cart')
        
        store_items = {}
        for item in cart_items:
            store = item.product.store_id
            if store not in store_items:
                store_items[store] = []
            store_items[store].append(item)
        
        store_subtotals = {
            store.store_id: sum(item.total_price for item in items)
            for store, items in store_items.items()
        }
        
        subtotal = cart.total_cost
        total = subtotal
        
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found.")
        return redirect('home')
    
    cart = request.user.cart
    total_quantity = sum(item.quantity for item in cart.items.all())
    
    context = {
        'cart': cart,
        'store_items': store_items,
        'store_subtotals': store_subtotals,
        'subtotal': subtotal,
        'total': total,
        'total_quantity':total_quantity
    }
    
    return render(request, 'checkout.html', context)


@login_required
def place_order(request):

    if request.method == 'POST':
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all().select_related('product')
            
            if not cart_items:
                messages.warning(request, "Your cart is empty.")
                return redirect('view_cart')
            

            store_items = {}
            for item in cart_items:
                store = item.product.store_id
                if store not in store_items:
                    store_items[store] = []
                store_items[store].append(item)
            
            
            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_cost,
                status='pending'
            )
            
            for store, items in store_items.items():
                store_total = sum(item.total_price for item in items) 
                
                store_order = StoreOrder.objects.create(
                    order=order,
                    store=store,
                    store_total=store_total,
                    status='pending'
                )
                
                for cart_item in items:
                    OrderItem.objects.create(
                        store_order=store_order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.product_price
                    )
            
            cart_items.delete()
            
            messages.success(request, "Your order has been placed successfully!")
            return redirect('home')
