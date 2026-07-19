from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category
from django.db.models import Q
from django.http import JsonResponse
from .cart import (
    add_to_cart, remove_from_cart, update_cart_quantity,
    get_cart_items, get_cart_total, get_cart_count
)

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, F
from .forms import CategoryForm
from .models import Category
from django.contrib.auth.models import User
from django.http import HttpResponse

def home(request):
    featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:12]
    context = {
        'products': featured_products,
    }
    return render(request, "home.html", context)

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
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query),
            is_available=True
        )
    else:
        products = Product.objects.none()
    return render(request, 'products/search_results.html', {'products': products, 'query': query})

def product_list(request):
    """Display all available products."""
    products = Product.objects.filter(is_available=True)
    return render(request, 'products/product_list.html', {'products': products})


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

def remove_from_cart_view(request, product_id):
    remove_from_cart(request, product_id)
    return redirect('cart')

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

from django.shortcuts import render, redirect
from django.contrib import messages


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



def reset_admin_password(request):
    user = User.objects.get(username="admin")
    user.set_password("Admin@12345")
    user.save()
    return HttpResponse("Password reset successfully")