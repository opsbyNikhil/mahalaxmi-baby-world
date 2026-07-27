from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    # path('cart/', views.cart, name='cart'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('search/', views.search_products, name='search'),            

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart_ajax, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_view, name='update_cart'),
    
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('checkout/', views.checkout, name='checkout'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path("my-orders/", views.my_orders, name="my_orders"),
    path('signup/', views.signup_view, name='signup'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path("reset-admin-password/", views.reset_admin_password),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/product/add/', views.dashboard_product_add, name='dashboard_product_add'),
    path('dashboard/product/<int:pk>/edit/', views.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/product/<int:pk>/delete/', views.dashboard_product_delete, name='dashboard_product_delete'),
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/category/add/', views.dashboard_category_add, name='dashboard_category_add'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/<int:pk>/', views.dashboard_order_detail, name='dashboard_order_detail'),

]