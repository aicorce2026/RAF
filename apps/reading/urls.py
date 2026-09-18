from django.urls import path
from . import views

app_name = "reading"

urlpatterns = [
    path('library/', views.my_library, name='my_library'),
    path('<int:pk>/', views.reader, name='reader'),
    path('<int:pk>/file/', views.pdf_file, name='pdf_file'),
    path('<int:pk>/progress/', views.progress_update, name='progress_update'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/<int:book_pk>/toggle/', views.favorite_toggle, name='favorite_toggle'),
]
