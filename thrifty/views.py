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
from django.contrib.contenttypes.models import ContentType



from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import EmailOTP  
import random

def generate_otp():
    return str(random.randint(100000, 999999))


def register(request):
    if request.method == "POST":
        print("Register POST triggered")
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('fullname', '').strip()

        first_name = full_name.split()[0] if full_name else ''
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        user_data_has_error = False

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email already exists')

        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, 'Password must be at least 5 characters')

        if not user_data_has_error:
            new_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  
            )

            otp = generate_otp()
            EmailOTP.objects.update_or_create(user=new_user, defaults={'otp': otp})

            # Send OTP to user's email
            send_mail(
                'Your Thriftify OTP Code',
                f'Hello {new_user.first_name},\n\nYour OTP for verifying your Thriftify account is: {otp}',
                'noreply@thriftify.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Account created! Check your email for the OTP to verify your account.')
            return redirect('verify_otp', user_id=new_user.id)

        else:
            return redirect('register')

    return render(request, 'register.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import EmailOTP

def verify_otp(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        try:
            otp_record = EmailOTP.objects.get(user=user)

            if otp_record.is_expired():
                messages.error(request, "OTP expired. Please register again.")
                user.delete()  # Clean up user
                otp_record.delete()
                return redirect('register')

            if entered_otp == otp_record.otp:
                user.is_active = True
                user.save()
                otp_record.delete()  # Clean up OTP record
                messages.success(request, "Your email has been verified. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        except EmailOTP.DoesNotExist:
            messages.error(request, "No OTP record found. Please register again.")
            return redirect('register')

    return render(request, 'verify_otp.html', {'user': user})



from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

@never_cache
@csrf_protect
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

    
 


from django.shortcuts import render
from .models import Product

def category_view(request, category_name):
    products = Product.objects.filter(category__iexact=category_name)
    return render(request, 'category.html', {'products': products, 'category': category_name})

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

def category_partial(request, category_name):
    page = int(request.GET.get('page', 1))
    all_products = Product.objects.filter(category__iexact=category_name)
    paginator = Paginator(all_products, 8)  # 10 products per page

    try:
        products = paginator.page(page)
    except:
        products = []

    html = render_to_string('partials/product_grid.html', {'products': products})
    return JsonResponse({'html': html, 'has_next': products.has_next()})


from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Increment view count
    product.view_count += 1
    product.save(update_fields=['view_count'])

    return render(request, 'product_detail.html', {'product': product})


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

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Product, CartItem  # adjust import as needed

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to your cart.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    product = get_object_or_404(Product, id=product_id)

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        if cart_item.quantity < product.quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in your cart.")
        else:
            messages.warning(request, f"Only {product.quantity} item(s) available in stock.")
    else:
        if product.quantity > 0:
            cart_item.quantity = 1
            cart_item.save()
            messages.success(request, f"{product.name} added to your cart.")
        else:
            cart_item.delete()  # Prevent creating item with 0 stock
            messages.warning(request, f"{product.name} is out of stock.")

    return redirect('view_cart')
 # Change to your cart view name if needed

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


from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from .models import Review, Product
from .forms import ReviewForm

User = get_user_model()

@login_required
def profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    profile = Profile.objects.filter(user=user_profile).first()
    products = Product.objects.filter(user=user_profile)
    content_type = ContentType.objects.get_for_model(User)
    
    # Get reviews left for this user
    reviews = Review.objects.filter(content_type=content_type, object_id=user_profile.id)

    # Handle review submission (only if reviewer != review target)
    form = None
    if request.user != user_profile:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.reviewer = request.user
                review.content_type = content_type
                review.object_id = user_profile.id
                review.save()
                messages.success(request, "Review added.")
                return redirect('user_profile', username=username)
        else:
            form = ReviewForm()

    return render(
        request,
        'profile.html' if request.user == user_profile else 'public_profile.html',
        {
            'user_profile': user_profile,
            'profile': profile,
            'products': products,
            'reviews': reviews,
            'form': form,
        }
    )




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile

@login_required
def edit_profile(request, username):
    if username != request.user.username:
        return redirect('user_profile', username=request.user.username)

    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})


from .models import Product

import joblib
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.contrib.contenttypes.models import ContentType
from thrifty.models import Product, Review 
from django.shortcuts import redirect
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    similar_products = []
    profile = None  # ✅ Initialize early to avoid UnboundLocalError

    try:
        # Load precomputed similarities
        recs_path = 'thrifty/data/content_recommendations.pkl'
        recommendations = joblib.load(recs_path)

        similar_ids = recommendations.get(str(product.product_id), [])
        similar_products = Product.objects.filter(product_id__in=similar_ids)

        if not similar_products:
            raise KeyError("No match found")

    except Exception:
        # Live fallback if precomputed fails
        all_products = Product.objects.exclude(id=product.id)
        corpus = [
            f"{product.name} {product.category} {product.description or ''}"
        ] + [
            f"{p.name} {p.category} {p.description or ''}" for p in all_products
        ]

        if len(corpus) > 1:
            vectorizer = TfidfVectorizer(stop_words='english')
            vectors = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

            top_indices = sims.argsort()[-4:][::-1]
            similar_products = [
                all_products[int(i)] for i in top_indices if sims[int(i)] > 0.1
            ]

    # ✅ Make sure this runs regardless of exception
    if product.user:
        profile = Profile.objects.filter(user=product.user).first()

        # Get reviews for this product using ContentType
    content_type = ContentType.objects.get_for_model(Product)
    reviews = Review.objects.filter(content_type=content_type, object_id=product.pk)
     # Handle Review Form submission
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
        
        if product.user == request.user:
            messages.error(request, "You cannot review your own product.")
            return redirect(product.get_absolute_url())

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.content_object = product
            review.save()
            return redirect(product.get_absolute_url())
    else:
        form = ReviewForm()

    return render(request, 'product_detail.html', {
        'product': product,
        'similar_products': similar_products,
        'reviews': reviews,
        'form': form,
        'seller_profile': profile,
    })

# views.py
from django.shortcuts import redirect

def product_redirect_by_id(request, id):
    product = get_object_or_404(Product, id=id)
    return redirect(product.get_absolute_url())

#chatbot
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chatbot_reply(request):
    if request.method == 'POST':
        try:
            # Parse JSON body
            body = json.loads(request.body)
            user_message = body.get('message')
            if not user_message:
                return JsonResponse({'reply': 'No message provided.'})

            # Send to Flask chatbot API
            response = requests.post(
                'http://localhost:5000/chat',
                json={'message': user_message}
            )
            data = response.json()
            return JsonResponse({'reply': data.get('reply')})
        except Exception as e:
            return JsonResponse({'reply': f'Error: {str(e)}'}, status=500)
    return JsonResponse({'reply': 'Invalid request'}, status=400)



from django.shortcuts import render

def chatbot_ui(request):
    return render(request, 'chatbot.html')
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

#uploading
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
@login_required
def upload_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('user_profile',username=request.user.username)
    else:
        form = ProductForm()
    return render(request, 'upload_product.html', {'form': form})


#edit_posts
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
def edit_product(request, username, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this product.")


    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=product.user.username)

    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})



from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # ✅ Only allow the user who uploaded it
    if product.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this product.")

    if request.method == "POST":
        product.delete()
        return redirect('user_profile', username=request.user.username)  # or any success page

    return redirect('product_detail', product.id)

@login_required
def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    products = Product.objects.filter(user=user_profile)

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'products': products,
    })


from django.shortcuts import render, get_object_or_404
from .models import Product, Review
from .forms import ReviewForm
from thrifty.models import Product  # adjust path as needed
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()

@login_required
def add_review(request, model_name, object_id):
    # Find the object being reviewed
    if model_name == 'product':
        target = get_object_or_404(Product, pk=object_id)
        if target.user == request.user:
            messages.error(request, "You cannot review your own product.")
            return redirect(target.get_absolute_url())
        
    elif model_name == 'user':
        target = get_object_or_404(User, pk=object_id)
        if target == request.user:
            messages.error(request, "You cannot review your own account.")
            return redirect('user_profile', username=request.user.username)
        
    else:
        return redirect('home')  # Or some fallback page

    # Get content type
    content_type = ContentType.objects.get_for_model(target)

    # Form handling
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.content_type = content_type
            review.object_id = object_id
            review.save()
            return redirect(request.POST.get('next') or target.get_absolute_url())
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'target': target
    })
    
from django.shortcuts import render
from .models import Product

def category_view(request, category_name):
    products = Product.objects.filter(category__iexact=category_name)
    return render(request, 'category_products.html', {'products': products, 'category_name': category_name})
from django.contrib.auth.decorators import login_required
from django.contrib import messages
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if review.reviewer != request.user:
        messages.error(request, "You are not authorized to edit this review.")
        return redirect(review.content_object.get_absolute_url())

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully.")
            return redirect(review.content_object.get_absolute_url())
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {'form': form, 'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.reviewer != request.user:
         return HttpResponseForbidden("You cannot delete this review.")

    if request.method == 'POST':
        url = review.content_object.get_absolute_url()
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect(url)

    return render(request, 'reviews/delete_review_confirm.html', {'review': review})


from django.contrib.auth import logout

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  # Log out the user before deleting
        user.delete()    # Deletes the user and any related data via cascading
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('home')  # Redirect to homepage or login page

    return render(request, 'delete_account.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem, Order, OrderItem  
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, OrderItem, CartItem, Product
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def checkout(request):
    if request.method == 'POST':
        address_type = request.POST.get('address-type', '').strip()
        full_address = request.POST.get('full-address', '').strip()
        phone = request.POST.get('number', '').strip()
        receiver_name = request.POST.get('receiver-name', '').strip()

        # Basic validation
        if not all([address_type, full_address, phone, receiver_name]):
            messages.error(request, "All fields are required.")
            return redirect('checkout')

        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('view_cart')

        # Create order
        order = Order.objects.create(
            user=request.user,
            address_type=address_type,
            address=full_address,
            phone=phone,
            receiver_name=receiver_name,
            status='Placed',
            order_date=timezone.now()
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Optional: reduce product quantity
            item.product.quantity -= item.quantity
            item.product.save()

        # Clear user's cart
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html')

@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    total_amount = sum(item.price * item.quantity for item in order_items)

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
        'total_amount': total_amount,
    })

from django.utils.timezone import now

@login_required
def purchased_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')

    for order in orders:
        time_elapsed = now() - order.order_date
        order.can_cancel = order.status == 'Placed' and time_elapsed.total_seconds() <= 1800

    return render(request, 'purchased_orders.html', {'orders': orders})


from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import Order, OrderItem

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    time_elapsed = now() - order.order_date

    if order.status != "Placed":
        messages.error(request, "Order cannot be cancelled.")
    elif time_elapsed.total_seconds() > 1800:
        messages.error(request, "You can only cancel within 30 minutes of placing the order.")
    else:
        for item in order.orderitem_set.all():
            product = item.product
            if product:
                product.quantity += item.quantity
                product.save()

        order.status = "Cancelled"
        order.save()

        messages.success(request, "Order has been cancelled and products restocked.")

    return redirect('purchased_orders')


def about(request):
    return render(request, 'about.html')
