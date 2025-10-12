from django import forms
from django.contrib.auth.models import User
from .models import Profile

# Класс: UserUpdateForm (CamelCase) для обновления основных данных пользователя
class UserUpdateForm(forms.ModelForm):
    # Поле: email (snake_case)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# Класс: ProfileUpdateForm (CamelCase) для обновления профиля и аватара
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        # Аватар обязателен при редактировании, как и при регистрации (см. models.py default)
        widgets = {
            'avatar': forms.FileInput(attrs={'required': 'required'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }