import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
import razorpay
from .models import FAQ, Cart, Product, Category, Order, OrderItem, Review, Wishlist
from .forms import ContactForm, NewsletterForm, UserRegistrationForm, CheckoutForm, ReviewForm
from django.contrib.auth import login, authenticate
from decimal import Decimal
from django.views.decorators.http import require_POST
from .models import  CartItem, Product, Wishlist
from django.db import transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Product, CartItem
import logging

logger = logging.getLogger(__name__)
def home(request):
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    new_products = Product.objects.filter(available=True).order_by('-created')[:8]
    categories = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)[:6]
    
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def product_list(request, category_slug=None):
    print("View called!")  # Debug statement
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    print(f"Initial products count: {products.count()}")  # Debug
    print("Initial products tttttttt",products)  # Debug
    
    if category_slug:
        print(f"Category slug: {category_slug}")  # Debug
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        print(f"Filtered products count: {products.count()}")  # Debug
    
    search_query = request.GET.get('search', '')
    if search_query:
        print(f"Search query: {search_query}")  # Debug
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        print(f"After search products count: {products.count()}")  # Debug
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(f"Page number: {page_number}")  # Debug
    
    # Add debug information for images
    for product in products:
        print(f"Product: {product.name}")
        print(f"Image exists: {bool(product.image)}")
        if product.image:
            print(f"Image URL: {product.image.url}")
            print(f"Image path: {product.image.path}")
            print(f"File exists: {os.path.exists(product.image.path)}")
    
    return render(request, 'product_list.html', {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'search_query': search_query
    })



def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been added!')
            return redirect('product_detail', id=id, slug=slug)
    else:
        review_form = ReviewForm()
    
    return render(request, 'detail.html', {
        'product': product,
        'related_products': related_products,
        'review_form': review_form
    })

@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    product_id_str = str(product.id)
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart')
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total_price = Decimal('0.00')
    
    for product in products:
        quantity = cart[str(product.id)]
        item_total = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': item_total
        })
        total_price += item_total
    
    return render(request, 'detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect('cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            # Calculate total
            products = Product.objects.filter(id__in=cart.keys())
            order.total = sum(
                product.price * cart[str(product.id)]
                for product in products
            )
            order.save()
            
            # Create order items
            for product in products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=cart[str(product.id)]
                )
            
            # Clear cart
            request.session['cart'] = {}
            messages.success(request, 'Your order has been placed successfully!')
            return render(request, 'success.html', {'order': order})
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'checkout.html', {'form': form})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f'{product.name} added to wishlist')
    return redirect('wishlist')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders.html', {'orders': orders})



def about(request):

    # return render(request,'about.html')
    return render(request, 'about.html',
                  

                  
                   {
        'title': 'About Us',
        'team_members': [
            {'name': 'John Doe', 'position': 'Founder & CEO', 'image': 'team/john.jpg'},
            {'name': 'Jane Smith', 'position': 'Marketing Director', 'image': 'team/jane.jpg'},
            {'name': 'Mike Johnson', 'position': 'Lead Developer', 'image': 'team/mike.jpg'},
        ],
        'company_stats': {
            'customers': 10000,
            'products': 500,
            'orders': 25000,
            'years': 5
        }
    })

def contact(request):
    """Contact page view with form submission"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email
            # send_mail(
            #     subject=f"Contact Form Submission from {form.cleaned_data['name']}",
            #     message=form.cleaned_data['message'],
            #     from_email=form.cleaned_data['email'],
            #     recipient_list=[settings.DEFAULT_FROM_EMAIL],
            #     fail_silently=False,
            # )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html'
                  
                  
                  , {
        'title': 'Contact Us',
        'form': form,
        'contact_info': {
            'address': '123 Main Street, City, Country',
            'phone': '+1 234 567 890',
            'email': 'info@onlinebazar.com',
            'hours': 'Monday-Friday: 9am-5pm'
        }
    })

def faq(request):
    """Frequently Asked Questions page view"""
    categories = FAQ.objects.values_list('category', flat=True).distinct()
    faqs = {}
    
    for category in categories:
        faqs[category] = FAQ.objects.filter(category=category)
    
    return render(request, 'faq.html', {
        'title': 'FAQs',
        'faqs': faqs
    })

def track_order(request):
    """Order tracking page view"""
    order = None
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        email = request.POST.get('email')
        
        try:
            order = Order.objects.get(id=order_id, email=email)
            messages.success(request, 'Order found!')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Please check your details.')
    
    return render(request, 'track_order.html', {
        'title': 'Track Your Order',
        'order': order
    })

def newsletter_subscribe(request):
    """Newsletter subscription view"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            return redirect('home')
    else:
        form = NewsletterForm()
    
    return render(request, 'newsletter_subscribe.html', {
        'title': 'Newsletter Subscription',
        'form': form
    })







def view_cart(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    cart_items = []
    subtotal = Decimal('0.00')
    
    if product_ids:
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            quantity = cart[str(product.id)]
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total,
                'id': product.id  # Using product ID since we don't have CartItem IDs
            })
            subtotal += item_total
    
    shipping = Decimal('0.00') if subtotal > 500 else Decimal('50.00')
    total = subtotal + shipping
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'cart.html', context)
# @login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # For both logged-in and anonymous users - use session cart
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"{product.name} added to your cart")
    
    # Redirect back to previous page or product detail
    redirect_url = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(redirect_url)


    

def order_success(request):
    """Display order success page"""
    return render(request, 'order_success.html')

def create_razorpay_order(request):
    """Create Razorpay order and return order ID"""
    if request.method == 'POST':
        try:
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Get amount from request (convert to paise)
            amount = int(float(request.POST.get('amount')))
            
            # Create order
            order_data = {
                'amount': amount,
                'currency': 'INR',
                'receipt': 'order_rcpt_123',
                'payment_capture': 1
            }
            order = client.order.create(data=order_data)
            
            return JsonResponse({
                'success': True,
                'order_id': order['id']
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@require_POST
def update_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': 1}
        )
        
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        
        cart_item.save()
        
        subtotal = cart.get_subtotal()
        tax = subtotal * Decimal('0.18')
        total = subtotal + tax
        
        return JsonResponse({
            'success': True,
            'new_quantity': cart_item.quantity,
            'item_total': float(cart_item.get_total()),
            'subtotal': float(subtotal),
            'tax': float(tax),
            'total': float(total),
            'item_count': cart.items.count()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def remove_from_cart(request, product_id):
    try:
        # Get the user's cart
        cart = Cart.objects.get(user=request.user)
        
        # Remove the item
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
        
        # Recalculate totals
        cart_items = CartItem.objects.filter(cart=cart)
        subtotal = sum(item.get_total() for item in cart_items)
        tax = subtotal * Decimal('0.18')  # 18% tax
        total = subtotal + tax
        
        return JsonResponse({
            'success': True,
            'item_count': cart_items.count(),
            'subtotal': float(subtotal),
            'tax': float(tax),
            'total': float(total)
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not in cart'}, status=404)
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart not found'}, status=404)
@require_POST
def save_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Item added to your wishlist'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Item already in your wishlist'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})