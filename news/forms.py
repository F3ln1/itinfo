from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import News


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Имя пользователя'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтверждение пароля'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Имя пользователя'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        })
    )


class NewsForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=News.CATEGORY_CHOICES,
        label='Категория',
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    class Meta:
        model = News
        fields = ['title', 'content', 'excerpt', 'image', 'category']
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'excerpt': 'Краткое описание',
            'image': 'Изображение',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Заголовок новости'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Содержание новости',
                'rows': 10
            }),
            'excerpt': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Краткое описание'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-input'
            }),
        }