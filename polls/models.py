import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Класс: Post (Вопрос для голосования) (CamelCase)
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Заголовок')

    # Поле: short_description (snake_case) - краткое описание для главной страницы
    short_description = models.CharField(max_length=300, verbose_name='Краткое описание')

    # Поле: full_description (snake_case) - полное описание
    full_description = models.TextField(verbose_name='Полное описание')

    # Изображение к посту (необязательно, blank=True)
    post_image = models.ImageField(upload_to='post_images/', blank=True, null=True, verbose_name='Изображение к посту')

    # Поле: creation_date (snake_case)
    creation_date = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')

    # Поле: expiration_date (snake_case) - Время жизни поста
    expiration_date = models.DateTimeField(verbose_name='Время жизни (до)')

    # Менеджер для фильтрации активных/неактивных постов
    # Активные посты: Expiration_date > now()
    objects = models.Manager()  # Стандартный менеджер

    # Класс: ActivePostManager (CamelCase)
    class ActivePostManager(models.Manager):
        def get_queryset(self):
            # Фильтрация: пост активен, если его время жизни еще не истекло
            return super().get_queryset().filter(expiration_date__gt=timezone.now())

    active_posts = ActivePostManager()  # Менеджер для активных постов

    def __str__(self):
        return self.title

    # Метод: is_active (snake_case)
    def is_active(self):
        # Проверка, активен ли пост
        return self.expiration_date > timezone.now()

    class Meta:
        ordering = ['-creation_date']


# Класс: VotingOption (Вариант ответа) (CamelCase)
class VotingOption(models.Model):
    # Связь с Post
    post = models.ForeignKey(Post, related_name='options', on_delete=models.CASCADE, verbose_name='Вопрос')
    option_text = models.CharField(max_length=150, verbose_name='Текст варианта')

    def __str__(self):
        return f'{self.post.title}: {self.option_text}'


# Класс: Vote (Голос) (CamelCase) - для ограничения голосования
class Vote(models.Model):
    # Поле: user (snake_case) - кто голосовал
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Поле: post (snake_case) - за какой пост
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # Поле: chosen_option (snake_case) - выбранный вариант
    chosen_option = models.ForeignKey(VotingOption, on_delete=models.CASCADE)

    # Ограничение: один пользователь - один голос за пост
    class Meta:
        # Уникальная комбинация user и post
        unique_together = ('user', 'post')
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'

    def __str__(self):
        return f'{self.user.username} проголосовал за {self.post.title}'

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
