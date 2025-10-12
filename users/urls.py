from django.urls import path
from . import views

urlpatterns = [
    # Главная страница профиля пользователя
    path('', views.profile_view, name='profile'),
    # Редактирование профиля
    path('edit/', views.profile_edit_view, name='profile_edit'),
    # Удаление профиля (испpip install django==4.2.0ользуем Django Auth для удаления)
    # path('delete/', views.profile_delete_view, name='profile_delete'),
]