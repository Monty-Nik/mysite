from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User

class Question(models.Question):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    short_description = models.TextField(verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    image = models.ImageField(upload_to='question_images/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    expires_at = models.DateTimeField(verbose_name="Действует до")  # Время жизни
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

class Choice(models.Choice):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Вопрос")
    choice_text = models.CharField(max_length=200, verbose_name="Текст варианта")
    votes = models.IntegerField(default=0, verbose_name="Голоса")

class Meta:
        unique_together = ('user', 'question')

class Vote(models.Model):
    """Модель для отслеживания голосов (1 голос на вопрос)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')  # Ограничение
class UserProfile(models.Model):
    """Профиль пользователя с обязательным аватаром"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name="Аватар")
    bio = models.TextField(blank=True, verbose_name="О себе")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


# Сигнал для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создает профиль при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Автоматически сохраняет профиль при сохранении пользователя"""
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

# Остальные модели (Question, Choice, Vote) остаются без изменений...