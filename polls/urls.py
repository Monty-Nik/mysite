from django.urls import path

from . import views
from django.urls import path
from . import views

# Имя приложения для пространства имен
app_name = 'polls'

urlpatterns = [
    # Главная страница: список активных постов
    path('', views.PostListView.as_view(), name='post_list'),
    # Создание нового поста
    path('create/', views.post_create_view, name='post_create'),
    # Детали поста и форма голосования
    path('<int:pk>/', views.post_detail_view, name='post_detail'),
    # Отображение результатов голосования (если отдельный URL нужен)
    # path('<int:pk>/results/', views.post_results_view, name='post_results'),
]

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
