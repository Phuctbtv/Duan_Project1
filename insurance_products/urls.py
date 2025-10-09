from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path('admin/', views.custom_products_admin, name='custom_products_admin'),
    path('user/products/', views.insurance_products_user, name='custom_products_user'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path("payment/<int:product_id>/", views.recent_products, name="buy_now"),

]
