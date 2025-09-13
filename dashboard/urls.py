from django.urls import path
from . import views
from django.urls import path, include
urlpatterns = [
    path('', views.admin_home, name='admin_home'),

]
