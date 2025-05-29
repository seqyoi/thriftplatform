from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import *
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import logout


def register(request):
    if request.method=="POST":   
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        full_name = request.POST.get('full_name', '').strip()

        first_name = full_name.split()[0] if full_name else ''
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        user_data_has_error = False
            # make sure email and username are not being used

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email already exists')

            # make aure password is at least 5 characters long
        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, 'Password must be at least 5 characters')

        if not user_data_has_error:
            new_user = User.objects.create_user(
             
                email = email,
                username = username,
                password = password,
                first_name=first_name,
               last_name=last_name
        )
            messages.success(request, 'Account created. Login now')
            return redirect('login')
        else:
            return redirect('register')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        # Getting user inputs from frontend
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Authenticate credentials
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                # Login user if credentials are correct
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')

        return redirect('login')  # on POST fail
    return render(request, 'login.html')  # on GET

#@login_required(login_url='login')  # restrict page to authenticated users
def home(request):
    return render(request, 'home.html')  # adjust template as needed

def logout_view(request):
    logout(request)
    return redirect('home')

def shop_view(request):
    return render(request,'product1.html')

 

