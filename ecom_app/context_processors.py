from .models import Category
from .cart import get_cart_count
from .models import Product

def categories(request):
    return {
        'categories': Category.objects.all()
    }



def cart_count(request):
    """Add cart count to all templates."""
    return {'cart_count': get_cart_count(request)}


def dashboard_categories(request):
    if not request.path.startswith('/dashboard/'):
        return {}
    categories = Category.objects.all().order_by('name')
    return {'sidebar_categories': categories}