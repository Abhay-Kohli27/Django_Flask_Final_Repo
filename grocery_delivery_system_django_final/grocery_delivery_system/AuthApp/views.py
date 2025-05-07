from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ProductsApp.urls import urlpatterns
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from functools import wraps
from .models import ContactMessage

User = get_user_model()


register_url = "http://127.0.0.1:5000/api/register"
login_url = "http://127.0.0.1:5000/api/login"
logout_url = "http://127.0.0.1:5000/api/logout"
current_user_url = "http://127.0.0.1:5000/api/user"

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'jwt_token' not in request.session:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def landing_page_view(request):
    return render(request, "landingpage.html")

@jwt_required
def home_view(request):
    return redirect('products')


def register_view(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        birth_date = request.POST.get('birth_date')
        profile_image = request.FILES.get('profile_image')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if password != cpassword:
            messages.error(request, 'Passwords do not match')

        register_data = {
            "username": username,
            "email":email,
            "mobile": phone_number,
            "password":password,
            "role":"user",
            "address":address,
            "birth_date" : str(birth_date)
        }

        register_response = requests.post(register_url, json=register_data)

        if register_response.status_code == 201:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    username=username,
                    phone_number=phone_number,
                    address=address,
                    birth_date=birth_date,
                    profile_image=profile_image,
                    password=password
                )
                messages.success(request, "User registered successfully!")
                return redirect('login')
            else:
                messages.warning(request, "Username already exists in Django DB.")
        else:
            print(f"registeration failed: {register_response.json().get("message")}")
    return render(request, 'login_register.html')
   


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        login_data = {
            "email": email,
            "password": password
        }

        login_response = requests.post(login_url, json=login_data)

        if login_response.status_code == 200:
            jwt_token = login_response.json().get('access_token')
            request.session['jwt_token'] = jwt_token
            messages.success(request, "User logged in through Flask API!")

            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, "User logged in successfully in Django!")

                if user.is_superuser or user.is_staff:
                    return redirect('/admin/')  
                else:
                    return redirect('home')    
            else:
                messages.warning(request, "Flask login worked, but user not found in Django.")
        else:
            messages.error(request, "Login failed: Invalid credentials or server error.")

    return render(request, 'login_register.html')


@jwt_required
def logout_view(request):
    headers_data = {
        'Authorization': f"Bearer {request.session.get('jwt_token', '')}",
        "Content-Type": "application/json"
    }

    logout_response = requests.get(logout_url, headers=headers_data)

    request.session.pop('jwt_token', None)


    if logout_response.status_code == 200:
        logout(request)
        messages.success(request, "User logged out successfully from both Flask and Django.")
    else:
        messages.warning(request, "Flask logout may have failed, but you were logged out of Django.")

    return redirect('landingpage')


@jwt_required
def user_profile_view(request):

    headers_data = {
        "Authorization":f"Bearer {request.session['jwt_token']}",
        "Content-Type":"application/json"
    }

    get_current_user_response = requests.get(current_user_url, headers=headers_data)
    response_data = get_current_user_response.json()
    current_user = response_data.get('current_user')

    if current_user is None:
        print("Error: 'current_user' not found in response.")
        print("Response data:", response_data)
    else:
        print("User:", current_user)
    return render(request, 'userprofile.html', context={"current_user" : current_user})



@login_required
def edit_profile(request):
    user = request.user  

    if request.method == 'POST':

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        messages.success(request, 'Profile image updated successfully!')
        return redirect('userprofile')  

    return redirect('userprofile')

def contact_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )

        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact') 
    return render(request, 'contact_us.html')



