from django import forms
from .models import Post, VotingOption


# Класс: PostCreateForm (CamelCase)
class PostCreateForm(forms.ModelForm):
    # Поле: expiration_date (snake_case) - время жизни поста
    # Используем DateTimeInput для удобства
    expiration_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Время жизни (дата и время истечения)'
    )

    # Поле для динамического добавления вариантов ответа
    # По умолчанию создадим 4 поля для вариантов ответа
    option_1 = forms.CharField(label='Вариант 1', max_length=150)
    option_2 = forms.CharField(label='Вариант 2', max_length=150)
    option_3 = forms.CharField(label='Вариант 3', max_length=150, required=False)
    option_4 = forms.CharField(label='Вариант 4', max_length=150, required=False)

    class Meta:
        model = Post
        # Исключаем 'author', который будет установлен в view
        fields = ['title', 'short_description', 'full_description', 'post_image', 'expiration_date']
        widgets = {
            'post_image': forms.FileInput,
            'full_description': forms.Textarea(attrs={'rows': 5}),
        }


# Класс: VoteForm (CamelCase) - форма для голосования
class VoteForm(forms.Form):
    # Поле: vote_option (snake_case) - будет содержать RadioSelect с вариантами
    vote_option = forms.ModelChoiceField(
        queryset=None,  # Установим в __init__
        widget=forms.RadioSelect,
        empty_label=None,
        label='Выберите ваш вариант'
    )

    # Функция: __init__ (snake_case)
    def __init__(self, *args, post=None, **kwargs):
        super().__init__(*args, **kwargs)
        if post:
            # Динамически устанавливаем queryset, чтобы отобразить варианты конкретного поста
            self.fields['vote_option'].queryset = VotingOption.objects.filter(post=post)