from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Класс: Profile (CamelCase)
class Profile(models.Model):
    # Связь с базовой моделью User (один к одному)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Поле: avatar (snake_case) - обязательное изображение
    # upload_to='avatars/' указывает папку для загрузки
    avatar = models.ImageField(
        default='avatars/default.jpg',  # Обязательный аватар, установим дефолтное изображение
        upload_to='avatars/',
        verbose_name='Аватар пользователя'
    )

    # Дополнительные поля, если нужны
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


# Функции-сигналы для автоматического создания/сохранения профиля при работе с User
# Функция: create_user_profile (snake_case)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Создаем Profile, если создан новый User
        Profile.objects.create(user=instance)


# Функция: save_user_profile (snake_case)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Сохраняем Profile при сохранении User
    instance.profile.save()