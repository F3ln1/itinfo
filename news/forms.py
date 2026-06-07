from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import News, Comment, Subscription


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


class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class PasswordResetCustomForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )


class SetPasswordCustomForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'subscribe_input',
                'placeholder': 'Ваш email',
            }),
        }


class CommentForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Комментарий',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Напишите комментарий...',
                'rows': 3,
            }),
        }