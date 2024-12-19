from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from django.contrib.auth.views import LogoutView
from .views import main_categories_view, add_main_category_view, edit_main_category_view, delete_main_category_view, \
    subcategories_view, add_subcategory_view, edit_subcategory_view, delete_subcategory_view, product_list_view, \
    add_product_view, edit_product_view, delete_product_view, \
    variant_list_view, add_variant_view, edit_variant_view, delete_variant_view


app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Default route for the custom admin panel
    path('api/daily-sales/', views.daily_sales_data, name='daily_sales_data'),  # Daily sales API
    path('api/weekly-orders/', views.weekly_order_data, name='weekly_order_data'),
    path('api/monthly-sales/', views.monthly_sales_data, name='monthly_sales_data'),
    path('login/', LoginView.as_view(template_name='admin/login.html'), name='admin_login'),
    path('logout/', LogoutView.as_view(), name='admin_logout'),

    path('main-categories/', main_categories_view, name='main_categories'),
    path('main-categories/add/', add_main_category_view, name='add_main_category'),
    path('main-categories/edit/<int:pk>/', edit_main_category_view, name='edit_main_category'),
    path('main-categories/delete/<int:pk>/', delete_main_category_view, name='delete_main_category'),

    path('subcategories/', subcategories_view, name='subcategories'),
    path('subcategories/add/', add_subcategory_view, name='add_subcategory'),
    path('subcategories/edit/<int:pk>/', edit_subcategory_view, name='edit_subcategory'),
    path('subcategories/delete/<int:pk>/', delete_subcategory_view, name='delete_subcategory'),

    path('products/', product_list_view, name='product_list'),
    path('products/add/', add_product_view, name='add_product'),
    path('products/edit/<int:pk>/', edit_product_view, name='edit_product'),
    path('products/delete/<int:pk>/', delete_product_view, name='delete_product'),

    path('variants/', variant_list_view, name='variant_list'),
    path('variants/add/', add_variant_view, name='add_variant'),
    path('variants/edit/<int:pk>/', edit_variant_view, name='edit_variant'),
    path('variants/delete/<int:pk>/', delete_variant_view, name='delete_variant'),


    # Inventory URLs
    path('inventories/', views.inventory_list_view, name='inventory_list'),
    path('inventories/add/', views.add_inventory_view, name='add_inventory'),
    path('inventories/edit/<int:pk>/', views.edit_inventory_view, name='edit_inventory'),
    path('inventories/delete/<int:pk>/', views.delete_inventory_view, name='delete_inventory'),

    # Variant Inventory URLs
    path('variant-inventories/', views.variant_inventory_list_view, name='variant_inventory_list'),
    path('variant-inventories/add/', views.add_variant_inventory_view, name='add_variant_inventory'),
    path('variant-inventories/edit/<int:pk>/', views.edit_variant_inventory_view, name='edit_variant_inventory'),
    path('variant-inventories/delete/<int:pk>/', views.delete_variant_inventory_view, name='delete_variant_inventory'),

    path('orders/', views.order_list_view, name='order_list'),
    path('orders/add/', views.add_order_view, name='add_order'),
    path('orders/edit/<int:pk>/', views.edit_order_view, name='edit_order'),
    path('orders/delete/<int:pk>/', views.delete_order_view, name='delete_order'),

    path('cart/', views.cart_list_view, name='cart_list'),
    path('cart/add/', views.add_cart_view, name='add_cart'),
    path('cart/edit/<int:pk>/', views.edit_cart_view, name='edit_cart'),
    path('cart/delete/<int:pk>/', views.delete_cart_view, name='delete_cart'),

    path('wishlist/', views.wishlist_list_view, name='wishlist_list'),
    path('wishlist/add/', views.add_wishlist_view, name='add_wishlist'),
    path('wishlist/edit/<int:pk>/', views.edit_wishlist_view, name='edit_wishlist'),
    path('wishlist/delete/<int:pk>/', views.delete_wishlist_view, name='delete_wishlist'),

    path('user/<int:user_id>/addresses/', views.user_addresses_view, name='user_addresses'),

    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blogs/add/', views.add_blog_view, name='add_blog'),
    path('blogs/edit/<int:pk>/', views.edit_blog_view, name='edit_blog'),
    path('blogs/delete/<int:pk>/', views.delete_blog_view, name='delete_blog'),

    path('banners/', views.banner_list_view, name='banner_list'),
    path('banners/add/', views.add_banner_view, name='add_banner'),
    path('banners/edit/<int:pk>/', views.edit_banner_view, name='edit_banner'),
    path('banners/delete/<int:pk>/', views.delete_banner_view, name='delete_banner'),

    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path('customers/edit/<int:pk>/', views.edit_customer_view, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer_view, name='delete_customer'),

    path('about/', views.about_list_view, name='about_list'),
    path('about/add/', views.add_about_view, name='add_about'),
    path('about/edit/<int:pk>/', views.edit_about_view, name='edit_about'),
    path('about/delete/<int:pk>/', views.delete_about_view, name='delete_about'),


]

