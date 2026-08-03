from django.contrib import admin
from .models import Cart, CartItem, BabyCategory, Category, Product
from django.utils.html import format_html

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

@admin.register(BabyCategory)
class BabyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'image_preview', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;border-radius:50%;object-fit:cover;" />',
                obj.image.url
            )
        return "—"
    image_preview.short_description = "Preview"
