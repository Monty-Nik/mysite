from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm, CustomUserCreationForm
from polls.models import Question  # Импортируем модель Question из приложения polls


def user_register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Профиль автоматически создается через сигнал

            # Аутентифицируем и логиним пользователя
            login(request, user)
            messages.success(request, f"Регистрация прошла успешно! Добро пожаловать, {user.username}!")
            return redirect('polls:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """Аутентификация пользователя"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Добро пожаловать, {username}!")
            return redirect('polls:index')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    return render(request, 'users/login.html')


@login_required
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect('polls:index')


@login_required
def profile_view(request):
    """Просмотр профиля пользователя"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Если профиль почему-то не создан, создаем его
        profile = UserProfile.objects.create(user=request.user)

    user_questions = Question.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'users/profile.html', {
        'profile': profile,
        'user_questions': user_questions
    })


@login_required
def profile_edit(request):
    """Редактирование профиля пользователя"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect('users:profile_view')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def profile_delete(request):
    """Удаление профиля пользователя"""
    if request.method == 'POST':
        # Получаем username для сообщения перед удалением
        username = request.user.username
        request.user.delete()
        logout(request)
        messages.success(request, f"Профиль пользователя {username} был успешно удален.")
        return redirect('polls:index')
    return render(request, 'users/profile_delete_confirm.html')