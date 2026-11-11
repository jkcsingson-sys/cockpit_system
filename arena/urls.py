from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry_view, name='entry'),
]