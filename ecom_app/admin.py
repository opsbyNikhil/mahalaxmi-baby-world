from django.contrib import admin
from .models import Category, Product
from .models import Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "brand",
        "price",
        "stock",
        "color",
        "is_available",
    )

    list_filter = (
        "category",
        "brand",
        "color",
        "is_available",
    )

    search_fields = (
        "name",
        "brand",
        "product_type",
        "theme",
        "package_includes"
    )

    list_editable = (
        "price",
        "stock",
        "is_available",   
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'item_count', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_key')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'subtotal')
    list_filter = ('product__category',)
    search_fields = ('product__name',)
