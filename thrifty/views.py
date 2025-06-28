from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
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
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import logout


def register(request):
    if request.method=="POST":   
        print("Login POST triggered") 
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
                print("Login successful")
                return redirect('home')
            else:
                print("Authentication failed"),
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            print("User does not exist")
            messages.error(request, 'Invalid email or password')

        return redirect('login')  # on POST fail
    return render(request, 'login.html')  # on GET

#@login_required(login_url='login')  # restrict page to authenticated users
# def home(request):
#     return render(request, 'home.html')  # adjust template as needed
import joblib
from .models import Product



def logout_view(request):
    logout(request)
    return redirect('home')

def shop_view(request):
    products = Product.objects.all().order_by('?')
    return render(request, 'shop.html', {'products': products})

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')
    return render(request,'forgot_password.html' )

def PasswordResetSent(request, reset_id):
    
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html',{'reset_id': reset_id})
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

def ResetPassword(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)

    
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')
 
from thrifty.models import Category

def category_list(request):
    categories = Category.objects.all().prefetch_related('images')
    return render(request, 'category_list.html', {'categories': categories})

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    images = CategoryImage.objects.filter(category=category)
    all_categories = Category.objects.all()
    return render(request, 'category_detail.html', {
        'category': category,
        'images': images,
        'all_categories': all_categories,
    })
# views.py
from django.shortcuts import get_object_or_404
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Increment view count
    product.view_count += 1
    product.save(update_fields=['view_count'])

    return render(request, 'product_detail.html', {'product': product})

def most_viewed_products_view(request):
    products = Product.objects.order_by('-view_count')[:10]
    return render(request, 'most_viewed.html', {'products': products})
# views.py
from .models import ProductView

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Increment total view count
    product.view_count += 1
    product.save(update_fields=['view_count'])

    # Track user-specific view
    if request.user.is_authenticated:
        ProductView.objects.get_or_create(user=request.user, product=product)

    return render(request, 'product_detail.html', {'product': product})




    #popularity based
import joblib
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from thrifty.models import Product
import pandas as pd 

#popularity based
import joblib
from django.shortcuts import render, get_object_or_404
from .models import Product  # Make sure this model exists

def popular_products_view(request):
    popular_ids = joblib.load('thrifty/data/popular_df.pkl')
    popular_ids = list(popular_ids.index)

    # Fetch Product objects matching those IDs
    products = Product.objects.filter(product_id__in=popular_ids)

    return render(request, 'thrifty/popular_products.html', {'products': products})
#content-based recs views
import pandas as pd
import joblib

def content_based_recommendations(request, product_id):
    df = joblib.load('thrifty/data/products_df.pkl')
    cosine_sim = joblib.load('thrifty/data/cosine_sim.pkl')

    df = df.reset_index(drop=True)
    indices = pd.Series(df.index, index=df['product_id'])

    if product_id not in indices:
        return render(request, 'thrifty/recommendations.html', {'error': 'Product not found.'})

    idx = indices[product_id]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # Top 5 similar

    recommended_ids = df.iloc[[i[0] for i in sim_scores]]['product_id'].tolist()
    recommended_products = Product.objects.filter(product_id__in=recommended_ids)

    return render(request, 'thrifty/recommendations.html', {'products': recommended_products})

def home_view(request):
    recommended_products = []
    try:
        popular_ids = joblib.load('thrifty/data/popular_df.pkl')  # This is already a list
        popular_ids = [str(pid).strip() for pid in popular_ids]   # Ensure string consistency

        print("Popular IDs:", popular_ids)
        products = Product.objects.filter(product_id__in=popular_ids)
    except Exception as e:
        print("Error loading popular products:", e)
        products = []
       

# Load content-based recommendations for a sample product (e.g., the first popular one)
      
    popular_ids = joblib.load('thrifty/data/popular_df.pkl')
    print(f"Popular IDs: {popular_ids}")

    # Load content-based recommenders
    try:
        cosine_sim = joblib.load('thrifty/data/cosine_sim.pkl')
        df = joblib.load('thrifty/data/products_df.pkl')

        # If cosine_sim is a DataFrame, convert to numpy array
        if hasattr(cosine_sim, 'values'):
            cosine_sim = cosine_sim.values

        # Create index mapping product_id to row index in df
        df['product_id'] = df['product_id'].astype(str).str.strip()
        indices = pd.Series(df.index, index=df['product_id']).to_dict()
        print(f"Indices sample keys: {list(indices.keys())[:10]}")

        # Pick a reference product id (for example, first popular)
        reference_pid = popular_ids[4]
        print(f"Reference PID: {reference_pid}")

        recommended_ids = []

        if reference_pid in indices:
            idx = indices[reference_pid]

            # cosine_sim[idx] should be a 1D array of similarity scores
            sim_scores = list(enumerate(cosine_sim[idx]))
            print(f"Sample sim_scores: {sim_scores[:5]}")
            print(f"Type of sim_scores[0][1]: {type(sim_scores[0][1])}")

            # Sort by similarity score descending and skip the first (itself)
            sim_scores = sorted(sim_scores, key=lambda x: float(x[1]), reverse=True)[1:6]

            sim_indices = [i[0] for i in sim_scores]
            recommended_ids = df.iloc[sim_indices]['product_id'].astype(str).tolist()
            print(f"Recommended IDs: {recommended_ids}")
        else:
            print(f"Reference PID {reference_pid} not found in indices")

    except Exception as e:
        print(f"Error loading content-based recommendations: {e}")
        recommended_ids = []

    # Fetch popular products from DB (filter by popular_ids)
    popular_products = Product.objects.filter(product_id__in=popular_ids)

    # Fetch recommended products from DB (filter by recommended_ids)
    recommended_products = Product.objects.filter(product_id__in=recommended_ids)

    context = {
        'popular_products': popular_products,
        'recommended_products': recommended_products,
    }
    return render(request, 'home.html', context)
from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Optional: Check if already in cart
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart') 

from .models import CartItem
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items if item.product.price)
    
    return render(request, 'view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item = CartItem.objects.filter(user=request.user, product=product).first()
    if item:
        item.delete()
        messages.success(request, f"{product.name} removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    # You can expand this with payment integration later
    messages.success(request, "Proceeding to checkout... (stub)")
    return redirect('view_cart')



from django.shortcuts import render, get_object_or_404
from .models import Profile, Post

def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    posts = Post.objects.filter(user=request.user)
    return render(request, 'profile.html', {'profile': profile, 'posts': posts})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # or your profile page url name
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

from .models import Product

import joblib
from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Load content-based recommendations
    try:
        recs_path = 'thrifty/data/content_recommendations.pkl'
        recommendations = joblib.load(recs_path)

        similar_ids = recommendations.get(str(product.product_id), [])  # Use product_id as string
        similar_products = Product.objects.filter(product_id__in=similar_ids)
    except Exception as e:
        similar_products = []

    return render(request, 'product_detail.html', {
        'product': product,
        'similar_products': similar_products,
    })


from django.shortcuts import render
from .models import Product  # make sure Product model exists

def search_products(request):
    query = request.GET.get('q')  # get the search term from the form
    products = []

    if query:
        products = Product.objects.filter(name__icontains=query)

    context = {
        'products': products,
        'query': query
    }
    return render(request, 'search_results.html', context)
