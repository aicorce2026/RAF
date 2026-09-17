from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("<int:pk>/", views.book_detail, name="book_detail"),
    path("authors/<int:pk>/", views.author_detail, name="author_detail"),
    path("categories/<int:pk>/", views.category_detail, name="category_detail"),
]
