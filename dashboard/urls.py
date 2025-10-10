# from django.urls import path
# from . import views
# from django.urls import path, include
# urlpatterns = [
#     path('', views.admin_home, name='admin_home'),
#
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('data/', views.dashboard_data, name='dashboard_data'),
]