from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Product

def get_or_create_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If we found a cart with session_key but now user is logged in, merge/clean
        if cart.session_key:
            cart.session_key = None
            cart.save()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id, quantity=1):
    """Add product to cart; update quantity if already exists."""
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += int(quantity)
    else:
        item.quantity = int(quantity)
    item.save()
    return cart

def remove_from_cart(request, product_id):
    """Remove a product from cart."""
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()

def update_cart_quantity(request, product_id, quantity):
    """Update quantity of a product in cart."""
    if quantity <= 0:
        remove_from_cart(request, product_id)
    else:
        cart = get_or_create_cart(request)
        item = CartItem.objects.get(cart=cart, product_id=product_id)
        item.quantity = int(quantity)
        item.save()

def get_cart_items(request):
    """Return queryset of CartItems for the current cart."""
    cart = get_or_create_cart(request)
    return cart.items.all()

def get_cart_total(request):
    """Return total price of all items in current cart."""
    cart = get_or_create_cart(request)
    return cart.total

def get_cart_count(request):
    """Return total number of items (sum of quantities) in current cart."""
    cart = get_or_create_cart(request)
    return cart.item_count