import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # Полное описание
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', null=True, blank=True)  # Время жизни поста
    image = models.ImageField(upload_to='posts/', blank=True, null=True)  # Изображение поста
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Автор поста

    def __str__(self):
        return self.question_text

    def is_active(self):
        """Проверяет, активен ли еще вопрос для голосования."""
        now = timezone.now()
        if self.end_date is None:
            return True
        return now <= self.end_date

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Vote(models.Model):
    """Модель для отслеживания, кто и за что голосовал."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'question']

# Сигналы для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    class Meta:
        # Один пользователь - один голос на вопрос
        unique_together = ['user', 'question']


class Profile(models.Model):
    # Связь "один-к-одному" с моделью User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Аватарка. upload_to указывает подпапку в MEDIA_ROOT. Validators можно добавить для проверки размера.
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # Дополнительные поля, если нужны (например, bio = models.TextField(max_length=500, blank=True))

    def __str__(self):
        return f'Profile of {self.user.username}'

# Сигналы для автоматического создания/обновления профиля при работе с User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



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
