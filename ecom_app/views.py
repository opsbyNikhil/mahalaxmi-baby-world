from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category
from django.db.models import Q
from django.http import JsonResponse
from .cart import (
    add_to_cart, remove_from_cart, update_cart_quantity,
    get_cart_items, get_cart_total, get_cart_count, clear_cart
)
from django.urls import reverse
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, F
from .forms import CategoryForm
from .models import Category
from .models import Customer
from .forms import SignUpForm
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
from .models import Order
from django.contrib.auth import login, logout, authenticate
import re
from .models import Product, Wishlist, BabyCategory
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags



# ---------- Auth ----------

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.POST.get('next') or request.GET.get('next') or 'home'

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []

        if not first_name:
            errors.append("Please enter your name.")

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            errors.append("Please enter a valid email address.")
        elif User.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")

        if not username:
            errors.append("Please choose a username.")
        elif User.objects.filter(username=username).exists():
            errors.append("That username is already taken.")

        if phone and not re.match(r'^\d{10}$', phone):
            errors.append("Phone number must be exactly 10 digits.")

        # ---- Password strength rules (mirrors the JS checklist) ----
        if len(password1) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password1):
            errors.append("Password must include at least one uppercase letter.")
        if not re.search(r'[a-z]', password1):
            errors.append("Password must include at least one lowercase letter.")
        if not re.search(r'[0-9]', password1):
            errors.append("Password must include at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/~`;\']', password1):
            errors.append("Password must include at least one special character.")

        if password1 != password2:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'auth/signup.html', {
                'next': next_url,
                'old': request.POST,
            })

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            password=make_password(password1),
        )
        Customer.objects.create(user=user, phone=phone)

        # No auto-login — send them to the login page instead
        messages.success(request, f"Account created successfully! Please sign in to continue, {first_name}.")

        login_url = reverse('login')
        return redirect(f'{login_url}?next={next_url}')

    return render(request, 'auth/signup.html', {'next': next_url})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.POST.get('next') or request.GET.get('next') or 'home'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'auth/login.html', {'next': next_url})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            # Give a more specific hint without leaking whether the
            # username exists (standard security practice)
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, "You've been signed out.")
    return redirect('home')

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'auth/forgot_password.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    html_email_template_name = 'auth/password_reset_email.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        # form_valid() is where Django actually saves the new password.
        # Call super() first so the password change happens, then send
        # the confirmation email using the now-saved user.
        response = super().form_valid(form)

        user = form.user  # the user whose password was just changed

        subject = 'Your password has been changed - Baby Store'
        message = render_to_string('auth/password_changed_email.html', {
            'user': user,
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,  # don't break the password reset flow if email fails
        )

        return response

# Replace CustomPasswordResetConfirmView in views.py with this version.
# Sends a proper HTML email (plain text fallback + HTML) using
# EmailMultiAlternatives, same approach Django uses internally for
# the reset-request email when html_email_template_name is set.




class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        # form_valid() is where Django actually saves the new password.
        # Call super() first so the password change happens, then send
        # the confirmation email using the now-saved user.
        response = super().form_valid(form)

        user = form.user

        login_url = self.request.build_absolute_uri(reverse('login'))

        html_content = render_to_string('auth/password_changed_email.html', {
            'user': user,
            'login_url': login_url,
        })
        text_content = strip_tags(html_content)  # plain-text fallback for clients that don't render HTML

        email = EmailMultiAlternatives(
            subject='Your password has been changed - Baby Store',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")

        try:
            email.send(fail_silently=False)
        except Exception:
            # Don't let an email failure break the password reset itself —
            # the password is already changed at this point regardless.
            pass

        return response

def home(request):
    featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:12]
    categories = BabyCategory.objects.filter(is_active=True)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        'products': featured_products,
        'categories': categories,
        'wishlist_ids': wishlist_ids,
    }
    return render(request, "home.html", context)

def category_products(request, slug):
    category = get_object_or_404(BabyCategory, slug=slug, is_active=True)
    products = Product.objects.filter(category__slug=slug, is_available=True)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_products.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_available=True)
    related = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    # Parse package includes into a list
    package_list = []
    if product.package_includes:
        # Split by comma, strip whitespace, and filter out empty items
        package_list = [
            item.strip() 
            for item in product.package_includes.split(',') 
            if item.strip()
        ]

    context = {
        'product': product,
        'related_products': related,
        'package_list': package_list,  
    }
    return render(request, 'products/product_detail.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'categories/category_products.html', context)


def search_products(request):
    query = request.GET.get('q', '').strip()

    if query:
        words = query.split()
        combined = Q()
        for word in words:
            combined &= (
                Q(name__icontains=word) |
                Q(description__icontains=word) |
                Q(brand__icontains=word)
            )
        products = Product.objects.filter(combined, is_available=True).distinct()
    else:
        products = Product.objects.none()
    return render(request, 'products/search_results.html', {'products': products, 'query': query})

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        words = query.split()
        combined = Q()
        for word in words:
            combined &= (
                Q(name__icontains=word) |
                Q(description__icontains=word) |
                Q(brand__icontains=word)
            )
        products = Product.objects.filter(combined, is_available=True).distinct()[:6]
        for p in products:
            results.append({
                'name': p.name,
                'price': str(p.price),
                'url': reverse('product_detail', args=[p.pk]),
                'image': p.image.url if p.image else '',
            })
    return JsonResponse({'results': results})

def product_list(request):
    """Display all available products."""
    products = Product.objects.filter(is_available=True)
    return render(request, 'products/product_list.html', {'products': products})

@login_required(login_url='login')
def cart_view(request):
    """Display cart page."""
    items = get_cart_items(request)
    total = get_cart_total(request)
    print("=== CART VIEW DEBUG ===")
    print("Items count:", items.count())
    for item in items:
        print(f"  - {item.product.name} x {item.quantity} = ₹{item.subtotal}")
    return render(request, 'cart/cart.html', {
        'cart_items': items,
        'total': total
    })


@login_required(login_url='login')
def add_to_cart_ajax(request):
    """AJAX endpoint to add to cart."""
    print("=== ADD TO CART AJAX ===")
    print("Method:", request.method)
    print("POST data:", request.POST)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        print(f"Product ID: {product_id}, Quantity: {quantity}")
        
        if product_id:
            try:
                add_to_cart(request, product_id, quantity)
                cart_count = get_cart_count(request)
                print(f"Cart count after add: {cart_count}")
                return JsonResponse({
                    'success': True,
                    'cart_count': cart_count,
                    'message': 'Added to cart!'
                })
            except Exception as e:
                print("ERROR:", str(e))
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='login')
def remove_from_cart_view(request, product_id):
    remove_from_cart(request, product_id)
    return redirect('cart')



@login_required(login_url='login')
def update_cart_view(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        update_cart_quantity(request, product_id, quantity)
    return redirect('cart')

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def products(request):
    return render(request, "products/product_list.html")


def cart(request):
    return render(request, "cart/cart.html")

# Add these to your existing views.py
# (adjust the import path for `messages` / `render` if you already import them elsewhere)


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_text = request.POST.get('message', '').strip()
        if not name or not email or not message_text:
            messages.error(request, "Please fill in your name, email, and message.")
            return redirect('contact')
        messages.success(request, "Thanks! We've received your message and will get back to you soon.")
        return redirect('contact')

    return render(request, 'contact.html')



@login_required(login_url='login')
def checkout(request):
    """Display checkout page with shipping form + order summary."""
    cart_items = get_cart_items(request)

    if not cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('cart')

    total = get_cart_total(request)

    context = {
        'checkout_items': cart_items,
        'total': total,
    }
    return render(request, 'cart/checkout.html', context)


@login_required(login_url='login')
def place_order(request):
    """Create the Order + OrderItems from the current cart, then clear it."""
    if request.method != 'POST':
        return redirect('checkout')

    cart_items = get_cart_items(request)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    payment_method = request.POST.get('payment_method', 'cod')

    if not all([full_name, phone, address, city, state, pincode]):
        messages.error(request, "Please fill in all shipping details.")
        return redirect('checkout')

    total = get_cart_total(request)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        phone=phone,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        payment_method=payment_method,
        total=total,
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
        )
        # Decrement stock
        product = item.product
        if product.stock:
            product.stock = max(0, product.stock - item.quantity)
            product.save(update_fields=['stock'])

    clear_cart(request)

    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('order_success', order_id=order.id)  # see note below

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart/my_orders.html', {'orders': orders})

@login_required(login_url='login')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'cart/order_success.html', {'order': order})


@login_required
def wishlist(request):
    """Show the logged-in user's wishlist."""
    wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist_obj.products.all()
    return render(request, 'products/wishlist.html', {
        'products': products,
    })


@login_required
def add_to_wishlist(request, product_id):
    """Add a product to the user's wishlist, then return to where they came from."""
    product = get_object_or_404(Product, id=product_id)
    wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_obj.products.add(product)
    messages.success(request, f"Added {product.name} to your wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def toggle_wishlist(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        in_wishlist = False
    else:
        in_wishlist = True

    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'wishlist_count': wishlist_count,
        'message': f"{'Added' if in_wishlist else 'Removed'} {product.name} {'to' if in_wishlist else 'from'} your wishlist.",
    })

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'cart/wishlist.html', context)

@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_obj.products.remove(product)
    messages.success(request, f"Removed {product.name} from your wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))

 
@login_required
def account_settings(request):
    """
    Renders the account settings page: profile details, password form,
    and saved addresses.
 
    Assumes an optional `Address` model with a ForeignKey to the user
    (e.g. `Address.objects.filter(user=request.user)`). If you don't
    have that model yet, `addresses` can stay an empty queryset/list —
    the template already handles the empty state.
    """
    try:
        from .models import Address
        addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-id')
    except ImportError:
        addresses = []
 
    context = {
        'addresses': addresses,
    }
    return render(request, 'cart/account_settings.html', context)
 
 
@login_required
def update_profile(request):
    """
    Updates first name, last name, email, and phone (if you have a
    Profile model with a `phone` field, e.g. via a OneToOneField on
    the user — adjust the profile lookup/creation to match your setup).
    """
    if request.method != 'POST':
        return redirect('account_settings')
 
    user = request.user
    user.first_name = request.POST.get('first_name', '').strip()
    user.last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
 
    if not email:
        messages.error(request, 'Email address is required.')
        return redirect('account_settings')
 
    user.email = email
    user.save()
 
    # Optional: only runs if you have a related Profile model with a
    # `phone` field. Remove this block if you store phone elsewhere,
    # or on the User model directly.
    phone = request.POST.get('phone', '').strip()
    profile = getattr(user, 'profile', None)
    if profile is not None:
        profile.phone = phone
        profile.save()
 
    messages.success(request, 'Profile updated successfully!')
    return redirect('account_settings')
 
 
@login_required
def change_password(request):
    """
    Changes the user's password using Django's built-in
    PasswordChangeForm (handles current-password verification,
    validators, and hashing) and keeps the session authenticated
    afterward via update_session_auth_hash.
    """
    if request.method != 'POST':
        return redirect('account_settings')
 
    form = PasswordChangeForm(
        user=request.user,
        data={
            'old_password': request.POST.get('current_password'),
            'new_password1': request.POST.get('new_password'),
            'new_password2': request.POST.get('confirm_password'),
        },
    )
 
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # keep the user logged in
        messages.success(request, 'Password updated successfully!')
    else:
        # Surface the first validation error (wrong current password,
        # passwords don't match, too weak, etc.)
        first_error = next(iter(form.errors.values()))[0]
        messages.error(request, first_error)
 
    return redirect('account_settings')
 
 
@login_required
def delete_account(request):

    if request.method != 'POST':
        return redirect('account_settings')
 
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, 'Your account has been deleted.')
    return redirect('home')
 

@staff_member_required
def dashboard_home(request):
    products = Product.objects.all().order_by('-id')

    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category__slug=selected_category)

    total_products = products.count()
    low_stock_count = products.filter(stock__lte=5, stock__gt=0).count()
    out_of_stock_count = products.filter(stock=0).count()
    total_inventory_value = products.aggregate(
        value=Sum(F('price') * F('stock'))
    )['value'] or 0

    context = {
        'products': products,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_inventory_value': total_inventory_value,
        'selected_category': selected_category,
    }
    return render(request, 'dashboard/dashboard_home.html', context)

@staff_member_required
def dashboard_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('dashboard_home')
    else:
        form = ProductForm()
    return render(request, 'dashboard/dashboard_product_form.html', {'form': form, 'is_edit': False})

@staff_member_required
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard_home')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/dashboard_product_form.html', {'form': form, 'is_edit': True, 'product': product})

@staff_member_required
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('dashboard_home')
    return render(request, 'dashboard/dashboard_product_confirm_delete.html', {'product': product})

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Invalid credentials or you do not have dashboard access.')

    return render(request, 'dashboard/dashboard_login.html')

def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')


@staff_member_required
def dashboard_category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('dashboard_home')
    else:
        form = CategoryForm()

    context = {'form': form, 'is_edit': False}
    return render(request, 'dashboard/dashboard_category_form.html', context)




@staff_member_required
def dashboard_orders(request):
    orders = Order.objects.all().order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    total_orders = Order.objects.count()
    pending_count = Order.objects.filter(status='pending').count()
    delivered_count = Order.objects.filter(status='delivered').count()
    total_revenue = Order.objects.aggregate(value=Sum('total'))['value'] or 0

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_count': pending_count,
        'delivered_count': delivered_count,
        'total_revenue': total_revenue,
        'selected_status': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/dashboard_orders.html', context)


@staff_member_required
def dashboard_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}.')
            return redirect('dashboard_order_detail', pk=order.pk)

    return render(request, 'dashboard/dashboard_order_detail.html', {'order': order})

def reset_admin_password(request):
    user = User.objects.get(username="admin")
    user.set_password("Admin@12345")
    user.save()
    return HttpResponse("Password reset successfully")

def get_dashboard_context(request, extra=None):
    """Shared sidebar context every dashboard page needs."""
    context = {
        'sidebar_categories': BabyCategory.objects.filter(is_active=True),
        'total_products': Product.objects.count(),
    }
    if extra:
        context.update(extra)
    return context


@staff_member_required
def dashboard_category_list(request):
    categories = BabyCategory.objects.all().order_by('display_order', 'name')
    context = get_dashboard_context(request, {'categories': categories})
    return render(request, 'dashboard/categories/category_list.html', context)

@staff_member_required
def dashboard_category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon', '')
        image = request.FILES.get('image')
        display_order = request.POST.get('display_order') or 0
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('dashboard_category_add')

        BabyCategory.objects.create(
            name=name,
            icon=icon,
            image=image,
            display_order=display_order,
            is_active=is_active,
        )
        messages.success(request, f'Category "{name}" added successfully.')
        return redirect('dashboard_category_list')

    context = get_dashboard_context(request, {'category': None})
    return render(request, 'dashboard/categories/category_form.html', context)


@staff_member_required
def dashboard_category_edit(request, pk):
    category = get_object_or_404(BabyCategory, pk=pk)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.icon = request.POST.get('icon', '')
        if request.FILES.get('image'):
            category.image = request.FILES.get('image')
        category.display_order = request.POST.get('display_order') or 0
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()

        messages.success(request, f'Category "{category.name}" updated successfully.')
        return redirect('dashboard_category_list')

    context = get_dashboard_context(request, {'category': category})
    return render(request, 'dashboard/categories/category_form.html', context)



@staff_member_required
def dashboard_category_delete(request, pk):
    category = get_object_or_404(BabyCategory, pk=pk)

    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('dashboard_category_list')

    context = get_dashboard_context(request, {'category': category})
    return render(request, 'dashboard/categories/category_confirm_delete.html', context)