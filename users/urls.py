from django.urls import path
from users.views import index, login_view

urlpatterns = [
    path('', index, name='trangchu'),
    path('login/', login_view, name='login'),
]