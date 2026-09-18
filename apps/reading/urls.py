from django.urls import path
from . import views

app_name = "reading"

urlpatterns = [
    path('<int:pk>/', views.reader, name='reader'),
    path('<int:pk>/file/', views.pdf_file, name='pdf_file'),
]
