from django.shortcuts import render,redirect
from StoreApp.models import Store
from ProductsApp.models import Product, ProductImage
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from UserApp.models import StoreOrder, OrderItem, Order
from django.db.models import Sum
import requests


current_user_url = "http://127.0.0.1:5000/api/user"


def manage_store_view(request, store_id):
    headers_data = {
        "Authorization": f"Bearer {request.session['jwt_token']}",
        "Content-Type": "application/json"
    }

    user = requests.get(current_user_url, headers=headers_data).json().get('current_user')

    store_url = f"http://127.0.0.1:5000/api/store/{store_id}"
    store = requests.get(store_url, headers=headers_data).json().get('store')

    django_store = Store.objects.get(store_id=store.get('id'))

    store_orders = StoreOrder.objects.filter(store_id=store.get('id'))
    total_sales = store_orders.aggregate(total=Sum('store_total'))['total'] or 0
    total_customers = store_orders.values('order__user').distinct().count()

    inventory_value = sum(
        product.product_price for product in Product.objects.filter(store_id=store_id)
    )

    return render(request, 'managestore.html', context={
        "user":user,
        "store": store,
        "store_orders": store_orders,
        "total_sales": total_sales,
        "total_customers": total_customers,
        "inventory_value": inventory_value,
        "django_store":django_store
    })


# def add_product_view(request, store_id):
#     store = get_object_or_404(Store, store_id=store_id)

#     if request.method == 'POST':
#         product_name = request.POST.get('product_name')
#         price = request.POST.get('product_price')
#         category = request.POST.get('product_category')
#         quantity = request.POST.get('product_quantity')
#         description = request.POST.get("product_description")
#         stock_threshold = request.POST.get("stock_threshold")
#         featured_product = bool(request.POST.get("featured_product"))

#         if not product_name or not price or not quantity or not category:
#             messages.error(request, 'All fields are required.')
#         elif int(price) <= 0:
#             messages.error(request, 'Price must be greater than zero.')
#         elif Product.objects.filter(product_name=product_name).exists():
#             messages.error(request, 'A product with this name already exists.')
#         else:
#             product = Product.objects.create(
#                 product_name=product_name,
#                 product_price=int(price),
#                 product_quantity=int(quantity),
#                 product_category=category,
#                 product_description=description,
#                 stock_threshold=int(stock_threshold),
#                 featured_product=featured_product,
#                 store_id=store
#             )

#             for image in request.FILES.getlist('product_images'):
#                 ProductImage.objects.create(product_id=product, image=image)

#             messages.success(request, "Product added successfully!")
#             return redirect('store_manage', store.store_id)

#     return render(request, 'managestore.html', {'store': store})



def add_product_view(request, store_id):
    headers_data = {
        "Authorization": f"Bearer {request.session['jwt_token']}",
        "Content-Type": "application/json"
    }

    store_url = f"http://127.0.0.1:5000/api/store/{store_id}"
    store = requests.get(store_url, headers=headers_data).json().get('store')

    django_store = Store.objects.get(store_id=store.get('id'))

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        price = request.POST.get('product_price')
        category = request.POST.get('product_category')
        quantity = request.POST.get('product_quantity')
        description = request.POST.get("product_description")
        stock_threshold = request.POST.get("stock_threshold")
        featured_product = bool(request.POST.get("featured_product"))

        if not product_name or not price or not quantity or not category:
            messages.error(request, 'All fields are required.')
        elif int(price) <= 0:
            messages.error(request, 'Price must be greater than zero.')
        elif Product.objects.filter(product_name=product_name).exists():
            messages.error(request, 'A product with this name already exists.')
        else:
            
            flask_api_url = "http://127.0.0.1:5000/api/product"
            flask_token = request.session.get('jwt_token')  
            headers = {
                "Authorization": f"Bearer {flask_token}",
                "Content-Type": "application/json"
            }

            flask_product_data = {
                "name": product_name,
                "category": category,
                "price": int(price),
                "quantity": int(quantity),
                "featured_product": featured_product,
                "image": None  
            }

            flask_response = requests.post(flask_api_url, json=flask_product_data, headers=headers)
            print(flask_response.json().get('message'))
            if flask_response.status_code == 201:
                product = Product.objects.create(
                    product_name=product_name,
                    product_price=int(price),
                    product_quantity=int(quantity),
                    product_category=category,
                    product_description=description,
                    stock_threshold=int(stock_threshold) if stock_threshold else 0,
                    featured_product=featured_product,
                    store_id=django_store
                )

                for image in request.FILES.getlist('product_images'):
                    ProductImage.objects.create(product_id=product, image=image)

                messages.success(request, "Product added and synced with Flask!")
            else:
                messages.warning(request, f"Product saved in Django but Flask sync failed: {flask_response.text}")

            return redirect('store_manage', store.get('id'))

    return render(request, 'managestore.html', {'store': store})



@login_required
def add_store_view(request):
    if request.method == "POST":
        store_name = request.POST.get('store_name')
        store_category = request.POST.get('store_category')
        store_description = request.POST.get('store_description')
        store_logo = request.FILES.get('store_logo')
        store_legal_business_name = request.POST.get('business_name')
        tax_number = request.POST.get('business_id')
        owner_name = request.POST.get('owner_name')
        business_email = request.POST.get('business_email')
        business_phone = request.POST.get('business_phone')

        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')
        store_address = f"{street_address}, {city}, {state} - {zip_code}"

        business_documentation = request.FILES.get('business_docs')

        if Store.objects.filter(user_id=request.user).exists():
            messages.error(request, "You have already submitted a store application.")
        else:
            
    
            flask_store_data = {
                "name": store_name,
                "category": store_category,
                "description": store_description,
                "deals": "",  
                "email": business_email,
                "location": store_address,
                "isapproved": False,
                "ownerid": request.user.id,  
                "store_key": 12345, 
                "owner_name": owner_name
            }

            jwt_token = request.session.get('jwt_token')
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }

            flask_store_register_url = "http://127.0.0.1:5000/api/store"
            response = requests.post(flask_store_register_url, json=flask_store_data, headers=headers)

            if response.status_code == 201:
                django_store = Store.objects.create(
                    user_id=request.user,
                    store_name=store_name,
                    store_category=store_category,
                    store_description=store_description,
                    store_logo=store_logo,
                    store_legal_business_name=store_legal_business_name,
                    tax_number=tax_number,
                    owner_name=owner_name,
                    business_email=business_email,
                    store_address=store_address,
                    business_documentation=business_documentation,
                    is_approved=False
                )
                messages.success(request, "Your store application has been submitted to both systems.")
            else:
                messages.warning(request, "Store saved in Django but failed to sync with Flask.")

            return redirect('products')

    return render(request, 'registerstore.html')



def view_store(request, store_id):
    store = Store.objects.get(store_id = store_id)
    cart = request.user.cart
    total_quantity = sum(item.quantity for item in cart.items.all())
    return render(request, 'store.html', context={"store":store,"total_quantity":total_quantity})


def update_store(request):
    store = get_object_or_404(Store, user_id=request.user)

    if request.method == 'POST':
        store.store_name = request.POST.get('store_name')
        store.owner_name = request.POST.get('store_owner')
        store.business_email = request.POST.get('store_email')
        store.store_description = request.POST.get('store_description')
        store.opening_time = request.POST.get('opening_time')
        store.closing_time = request.POST.get('closing_time')

        
        street_address = request.POST.get('street_address')
        city = request.POST.get('store_city')
        state = request.POST.get('store_state')
        zip_code = request.POST.get('store_zip')
        if (street_address and city and state and zip_code):
            store.store_address = f"{street_address}, {city}, {state} - {zip_code}"
        else:
            store.store_address = request.POST.get('store_address')

        store_category = request.POST.get('store_category')
        if store_category:
            store.store_category = store_category

        tax_number = request.POST.get('tax_number')
        if tax_number:
            store.tax_number = tax_number

        website = request.POST.get('website')
        if website:
            store.website = website

        if 'store_logo' in request.FILES:
            store.store_logo = request.FILES['store_logo']
        if 'business_documentation' in request.FILES:
            store.business_documentation = request.FILES['business_documentation']

        store.save()
        return redirect('store_manage', store_id=request.user.store.store_id)  
    
    return render(request, 'managestore.html', {'store': store})