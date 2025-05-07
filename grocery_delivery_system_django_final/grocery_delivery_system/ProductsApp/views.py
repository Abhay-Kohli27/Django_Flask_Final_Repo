from django.shortcuts import render, redirect
from ProductsApp.models import Product,ProductImage, Review
from django.contrib.auth.decorators import login_required
from StoreApp.models import Store
from django.contrib import messages
from django.db.models import Q
from UserApp.models import Cart, CartItem
from functools import wraps
import requests


products_url = "http://127.0.0.1:5000/api/products"
stores_url = "http://127.0.0.1:5000/api/stores"
current_user_url = "http://127.0.0.1:5000/api/user"


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'jwt_token' not in request.session:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# @jwt_required
# def show_products_view(request):
#     headers_data = {
#         'Authorization': f"Bearer {request.session['jwt_token']}",
#         "Content-Type": "application/json"
#     }

#     user = requests.get(current_user_url, headers=headers_data).json().get('current_user')

#     all_stores_response = requests.get(stores_url, headers=headers_data)
#     stores = all_stores_response.json().get('stores', [])

#     stores_with_products = []

#     for store in stores:
#         id = store['id']
#         store_products_url = f"http://127.0.0.1:5000/api/store/{id}/products"
#         products_response = requests.get(store_products_url, headers=headers_data)

#         all_products_response = requests.get(products_url, headers=headers_data)
#         all_products = all_products_response.json().get('products')
#         print(all_products)

#         all_django_products = Product.objects.all()

#         if products_response.status_code == 200:
#             products = products_response.json().get('products', [])
#         else:
#             products = []

#         stores_with_products.append({
#             "store": store,
#             "products": products
#         })
    
#     if hasattr(request.user, 'cart'):
#         cart = request.user.cart
#         total_quantity = sum(item.quantity for item in cart.items.all())
#     else:
#         total_quantity = 0
#         cart = Cart.objects.create(user=request.user)


#     return render(request, 'home.html', context={'stores_with_products': stores_with_products, 'user':user, 'total_quantity':total_quantity, "all_products":all_django_products})


@login_required()
def show_products_view(request):
    headers_data = {
        'Authorization': f"Bearer {request.session['jwt_token']}",
        "Content-Type": "application/json"
    }

    user = requests.get(current_user_url, headers=headers_data).json().get('current_user')

    all_stores_response = requests.get(stores_url, headers=headers_data)
    stores = all_stores_response.json().get('stores', [])

    stores_with_products = []

    for store in stores:
        flask_store_id = store['id']

        store_products_url = f"http://127.0.0.1:5000/api/store/{flask_store_id}/products"
        products_response = requests.get(store_products_url, headers=headers_data)
        flask_products = products_response.json().get('products', []) if products_response.status_code == 200 else []

        django_products = Product.objects.filter(store_id__store_id=flask_store_id)

        stores_with_products.append({
            "store": store,
            "flask_products": flask_products,
            "django_products": django_products
        })

    all_django_products = Product.objects.all()


    if hasattr(request.user, 'cart'):
        cart = request.user.cart
        total_quantity = sum(item.quantity for item in cart.items.all())
    else:
        cart = Cart.objects.create(user=request.user)
        total_quantity = 0

    return render(request, 'home.html', {
        'stores_with_products': stores_with_products,
        'user': user,
        'total_quantity': total_quantity,
        "all_products":all_django_products
    })




def show_individual_product(request, product_id):
    product = Product.objects.get(product_id=product_id)
    cart = request.user.cart
    total_quantity = sum(item.quantity for item in cart.items.all())
    reviews = Review.objects.filter(product=product)
    sum_of_ratings = 0
    for review in reviews:
        sum_of_ratings += review.rating
    avg_rating = sum_of_ratings / reviews.count() if reviews.exists() else 0
    return render(request, 'productspage.html', context={'product':product,'total_quantity':total_quantity, "reviews":reviews, "avg_rating":avg_rating })

def delete_product(request, product_id):
    product = Product.objects.get(product_id=product_id)
    

    flask_api_url = f"http://127.0.0.1:5000/api/product/{product_id}"
    jwt_token = request.session.get("jwt_token")

    if jwt_token:
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        flask_response = requests.delete(flask_api_url, headers=headers)

        if flask_response.status_code == 200:
            product.delete()
            messages.success(request, "Product deleted from both systems successfully.")
        else:
            messages.warning(request, f"Product not deleted Flask deletion failed with status {flask_response.status_code}.")
    else:
        messages.warning(request, "JWT token not found. Product deleted only from Django.")

    return redirect('store_manage', store_id=request.user.store.store_id)





def update_product(request, product_id):
    product = Product.objects.get(product_id=product_id)
    cart = request.user.cart
    total_quantity = sum(item.quantity for item in cart.items.all())

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.product_category = request.POST.get('product_category')
        product.product_price = request.POST.get('product_price')
        product.product_quantity = request.POST.get('product_quantity')
        product.product_description = request.POST.get('product_description')
        product.stock_threshold = request.POST.get('stock_threshold') or None
        product.featured_product = True if request.POST.get('featured_product') == 'featured_product' else False
        product.save()

        if request.FILES.getlist('product_images'):
            ProductImage.objects.filter(product_id=product).delete()
            for image in request.FILES.getlist('product_images')[:4]:
                ProductImage.objects.create(product_id=product, image=image)

        jwt_token = request.session.get('jwt_token')  
        if jwt_token:
            flask_api_url = f"http://127.0.0.1:5000/api/product/{product_id}"  
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "name": product.product_name,
                "category": product.product_category,
                "price": product.product_price,
                "quantity": product.product_quantity
            }
            response = requests.put(flask_api_url, json=payload, headers=headers)
            if response.status_code != 200:
                messages.warning(request, f"Flask API update failed: {response.json().get('message')}")

        messages.success(request, "Product was updated successfully")
        return redirect('store_manage', store_id=request.user.store.store_id)

    return render(request, 'updateproduct.html', context={'product': product, 'total_quantity': total_quantity})




def search_products(request):
    query = request.GET.get('q')
    product_results = []
    store_results = []

    if query:
        product_results = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_category__icontains=query) |
            Q(store_id__store_name__icontains=query)
        ).distinct()

        store_results = Store.objects.filter(
            Q(store_name__icontains=query)
        ).distinct()

    cart = request.user.cart
    total_quantity = sum(item.quantity for item in cart.items.all())

    return render(request, 'search_results.html', {
        'query': query,
        'product_results': product_results,
        'store_results': store_results,
        'total_quantity':total_quantity
    })




@login_required
def submit_review(request, product_id):
   
    product = Product.objects.get(product_id=product_id)    

    existing_review = Review.objects.filter(user=request.user, product=product).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, 'Please provide both rating and comment.')
            return render(request, 'submit_review.html', {'product': product})
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5.")
        except ValueError:
            messages.error(request, 'Rating must be a number between 1 and 5.')
            return render(request, 'submit_review.html', {'product': product})
        
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'Your review has been updated successfully!')
        else:
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Thank you for your review!')
        
        return redirect('show_individual_product', product_id=product_id)
    
    context = {
        'product': product,
        'existing_review': existing_review
    }
    return render(request, 'reviewpage.html', context)