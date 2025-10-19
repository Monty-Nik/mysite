from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Question, Choice, Vote, Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, QuestionForm  # Используем полную форму

@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)  # Полная форма
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.author = request.user
            new_question.save()
            return redirect('polls:detail', question_id=new_question.id)
    else:
        form = QuestionForm()

def index(request):
    """Главная страница. Показывает только активные вопросы."""
    now = timezone.now()
    # Фильтруем вопросы: либо end_date в будущем, либо end_date не установлен
    active_questions = Question.objects.filter(
        end_date__gte=now
    ) | Question.objects.filter(end_date__isnull=True)

    # Сортируем по дате публикации (новые сначала)
    active_questions = active_questions.order_by('-pub_date')

    context = {'question_list': active_questions}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # Проверяем, голосовал ли уже пользователь
    user_vote = None
    if request.user.is_authenticated:
        try:
            user_vote = Vote.objects.get(user=request.user, question=question)
        except Vote.DoesNotExist:
            pass
    context = {
        'question': question,
        'user_vote': user_vote, # Передаем в шаблон, чтобы показать выбранный вариант
    }
    return render(request, 'polls/detail.html', context)


@login_required
def create_question(request):
    """Представление для создания нового вопроса"""
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.author = request.user
            new_question.save()
            return redirect('polls:detail', question_id=new_question.id)
    else:
        form = QuestionForm()

    context = {'form': form}
    return render(request, 'polls/create_question.html', context)
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # Рассчитываем проценты для каждого варианта
    total_votes = sum(choice.votes for choice in question.choice_set.all())
    for choice in question.choice_set.all():
        if total_votes > 0:
            choice.percentage = round((choice.votes / total_votes) * 100, 2)
        else:
            choice.percentage = 0
    context = {'question': question, 'total_votes': total_votes}
    return render(request, 'polls/results.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES) # request.FILES для аватара
        if form.is_valid():
            user = form.save()
            # Сохраняем аватар в профиль
            user.profile.avatar = form.cleaned_data.get('avatar')
            user.profile.save()
            login(request, user) # Автоматически логиним пользователя после регистрации
            return redirect('polls:index') # Замените 'index' на имя вашего главного URL
    else:
        form = UserRegisterForm()
    return render(request, 'polls/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES, # Важно: для обновления изображения
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('polls:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'polls/profile.html', context)

@login_required
def delete_profile(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('polls:index') # Редирект после удаления
    return render(request, 'polls/delete_profile_confirm.html')

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'вы не сделали выбор'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


@login_required
def create_question(request):
    """Представление для создания нового вопроса"""
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.author = request.user
            new_question.save()
            return redirect('polls:detail', question_id=new_question.id)
    else:
        form = QuestionForm()

    context = {'form': form}
    return render(request, 'polls/create_question.html', context)