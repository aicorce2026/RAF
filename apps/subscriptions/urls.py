from django.urls import path
from . import views

app_name = "subscriptions"

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('request/', views.request_create, name='request_create'),
]
