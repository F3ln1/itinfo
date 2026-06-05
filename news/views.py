from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
import time
from .models import News, SavedNews
from .forms import RegisterForm, LoginForm, NewsForm


class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = News.objects.filter(status='published')
        category = self.request.GET.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        author = self.request.GET.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ['it', 'science', 'tech']
        context['current_category'] = self.request.GET.get('category', 'all')
        context['current_author'] = self.request.GET.get('author', '')
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    
    def get_object(self):
        obj = super().get_object()
        viewed = self.request.session.get('viewed_news', [])
        if obj.id not in viewed:
            obj.views += 1
            obj.save(update_fields=['views'])
            viewed.append(obj.id)
            self.request.session['viewed_news'] = viewed
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = self.get_object()
        context['related_news'] = News.objects.filter(
            category=news.category,
            status='published'
        ).exclude(id=news.id)[:3]
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedNews.objects.filter(
                user=self.request.user,
                news=news
            ).exists()
        return context


def home(request):
    news_list = News.objects.filter(status='published')[:6]
    featured_news = News.objects.filter(status='published').first()
    return render(request, 'news/home.html', {
        'news_list': news_list,
        'featured_news': featured_news,
    })


class RegisterView(SuccessMessageMixin, FormView):
    template_name = 'news/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('news:home')
    success_message = 'Регистрация прошла успешно!'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('news:home')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_list'] = News.objects.filter(status='published')[:6]
        context['featured_news'] = News.objects.filter(status='published').first()
        return context


class LoginUserView(SuccessMessageMixin, LoginView):
    template_name = 'news/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('news:home')
    success_message = 'Вы вошли в аккаунт!'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('news:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_list'] = News.objects.filter(status='published')[:6]
        context['featured_news'] = News.objects.filter(status='published').first()
        return context


def logout_user(request):
    logout(request)
    return redirect('news:home')


class ProfileView(ListView):
    model = News
    template_name = 'news/profile.html'
    context_object_name = 'user_news'

    def get_queryset(self):
        return News.objects.filter(author=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_news = context['object_list']
        saved = SavedNews.objects.filter(user=self.request.user).select_related('news')
        pending = user_news.filter(status='pending')
        published = user_news.filter(status='published')
        rejected = user_news.filter(status='rejected')
        context.update({
            'pending_news': pending[:6],
            'pending_count': pending.count(),
            'published_news': published[:6],
            'published_count': published.count(),
            'rejected_news': rejected[:6],
            'rejected_count': rejected.count(),
            'saved_news': saved[:6],
            'saved_count': saved.count(),
        })
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('news:login')
        return super().get(request, *args, **kwargs)


def save_news(request, slug):
    if not request.user.is_authenticated:
        return redirect('news:login')
    news = get_object_or_404(News, slug=slug)
    SavedNews.objects.get_or_create(user=request.user, news=news)
    return redirect('news:news_detail', slug=slug)


def unsave_news(request, slug):
    if not request.user.is_authenticated:
        return redirect('news:login')
    news = get_object_or_404(News, slug=slug)
    SavedNews.objects.filter(user=request.user, news=news).delete()
    return redirect('news:news_detail', slug=slug)


class CreateNewsView(SuccessMessageMixin, FormView):
    template_name = 'news/create_news.html'
    form_class = NewsForm
    success_url = reverse_lazy('news:profile')
    success_message = 'Новость отправлена на модерацию!'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('news:login')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_list'] = News.objects.filter(status='published')[:6]
        context['featured_news'] = News.objects.filter(status='published').first()
        return context

    def form_valid(self, form):
        news = form.save(commit=False)
        news.author = self.request.user
        news.status = 'pending'
        news.slug = slugify(news.title) or f'news-{int(time.time())}'
        base_slug = news.slug
        counter = 1
        while News.objects.filter(slug=news.slug).exists():
            news.slug = f"{base_slug}-{counter}"
            counter += 1
        news.save()
        return super().form_valid(form)
