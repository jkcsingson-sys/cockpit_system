from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.entry_view, name='entry'),
    path('logout/', LogoutView.as_view(), name='logout'),
]