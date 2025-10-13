from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path('admin/products/', views.custom_products_admin, name='custom_products_admin'),
    path('user/products/', views.insurance_products_user, name='custom_products_user'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('admin/products/add/', views.add_product_view, name='add_product'),
    path('admin/products/edit/<int:product_id>/', views.edit_product_view, name='edit_product'),


]
