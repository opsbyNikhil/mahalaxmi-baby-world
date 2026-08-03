from django.urls import path
from . import views
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views


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
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/settings/update-profile/', views.update_profile, name='update_profile'),
    path('account/settings/change-password/', views.change_password, name='change_password'),
    path('account/settings/delete/', views.delete_account, name='delete_account'),


    path('signup/', views.signup_view, name='signup'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('accounts/reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),



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

    path('dashboard/categories/', views.dashboard_category_list, name='dashboard_category_list'),
    path('dashboard/categories/add/', views.dashboard_category_add, name='dashboard_category_add'),
    path('dashboard/categories/<int:pk>/edit/', views.dashboard_category_edit, name='dashboard_category_edit'),
    path('dashboard/categories/<int:pk>/delete/', views.dashboard_category_delete, name='dashboard_category_delete'),
]