from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Question, Choice, UserProfile, Vote
from .forms import UserProfileForm, QuestionForm, CustomUserCreationForm
from users.models import UserProfile



def index(request):
    """Главная страница с активными вопросами"""
    now = timezone.now()
    # Показываем только активные, не истекшие вопросы
    questions = Question.objects.filter(is_active=True, expires_at__gt=now).order_by('-created_at')
    return render(request, 'polls/index.html', {'questions': questions})


def question_detail(request, question_id):
    """Детальная страница вопроса"""
    question = get_object_or_404(Question, id=question_id)

    # Проверяем, голосовал ли уже пользователь
    user_voted = False
    if request.user.is_authenticated:
        user_voted = Vote.objects.filter(user=request.user, question=question).exists()

    return render(request, 'polls/question_detail.html', {
        'question': question,
        'user_voted': user_voted
    })


@login_required
def vote(request, question_id):
    """Обработка голосования с проверкой ограничений"""
    question = get_object_or_404(Question, id=question_id)

    # Проверяем, не голосовал ли уже пользователь
    if Vote.objects.filter(user=request.user, question=question).exists():
        messages.error(request, "Вы уже голосовали в этом опросе!")
        return redirect('question_detail', question_id=question_id)

    # Проверяем, не истекло ли время голосования
    if question.is_expired():
        messages.error(request, "Время голосования в этом опросе истекло!")
        return redirect('question_detail', question_id=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "Вы не выбрали вариант ответа.")
        return redirect('question_detail', question_id=question_id)
    else:
        selected_choice.votes += 1
        selected_choice.save()

        # Сохраняем информацию о голосовании
        Vote.objects.create(user=request.user, question=question, choice=selected_choice)
        messages.success(request, "Ваш голос учтен!")
        return redirect('question_results', question_id=question.id)


def question_results(request, question_id):
    """Страница результатов с процентами"""
    question = get_object_or_404(Question, pk=question_id)
    total_votes = sum(choice.votes for choice in question.choice_set.all())

    # Рассчитываем проценты для каждого варианта
    choices_with_percent = []
    for choice in question.choice_set.all():
        percent = (choice.votes / total_votes * 100) if total_votes > 0 else 0
        choices_with_percent.append({
            'choice': choice,
            'percent': round(percent, 1)
        })

    return render(request, 'polls/results.html', {
        'question': question,
        'choices_with_percent': choices_with_percent,
        'total_votes': total_votes
    })


def user_register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль для нового пользователя
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'polls/register.html', {'form': form})


def user_login(request):
    """Аутентификация пользователя"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Добро пожаловать, {username}!")
            return redirect('index')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    return render(request, 'polls/login.html')


@login_required
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect('index')


@login_required
def profile_view(request):
    """Просмотр профиля пользователя"""
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'polls/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    """Редактирование профиля пользователя"""
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'polls/profile_edit.html', {'form': form})


@login_required
def profile_delete(request):
    """Удаление профиля пользователя"""
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        messages.success(request, "Ваш профиль был успешно удален.")
        return redirect('index')
    return render(request, 'polls/profile_delete_confirm.html')


@login_required
def question_create(request):
    """Создание нового вопроса"""
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            messages.success(request, "Вопрос успешно создан!")
            return redirect('question_detail', question_id=question.id)
    else:
        form = QuestionForm()
    return render(request, 'polls/question_create.html', {'form': form})