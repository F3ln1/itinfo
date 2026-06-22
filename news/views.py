from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, UpdateView, DeleteView, TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import time
from django.contrib.auth.models import User
from .models import News, SavedNews, Comment, Subscription, Notification
from .forms import RegisterForm, LoginForm, NewsForm, CommentForm


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
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(excerpt__icontains=q)
            )
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ['it', 'science', 'tech']
        context['current_category'] = self.request.GET.get('category', 'all')
        context['current_author'] = self.request.GET.get('author', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
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
        context['comments'] = news.comments.select_related('author').prefetch_related('replies__author').all()
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['is_saved'] = SavedNews.objects.filter(
                user=self.request.user,
                news=news
            ).exists()
        return context


def home(request):
    news_qs = News.objects.filter(status='published')
    news_list = news_qs[:6]
    featured_news = news_qs.first()
    total_authors = User.objects.filter(news__status='published').distinct().count()
    total_readers = User.objects.count()
    return render(request, 'news/home.html', {
        'news_list': news_list,
        'featured_news': featured_news,
        'total_news': news_qs.count(),
        'total_authors': total_authors,
        'total_readers': total_readers,
    })


CATEGORY_INFO = {
    'it': {'name': 'IT-технологии', 'description': 'Программирование, AI, облачные технологии', 'icon': 'computer'},
    'science': {'name': 'Наука', 'description': 'Исследования, открытия, космос', 'icon': 'science'},
    'tech': {'name': 'Техника', 'description': 'Гаджеты, робототехника, электроника', 'icon': 'tech'},
}


def categories(request):
    cats = []
    for key, info in CATEGORY_INFO.items():
        count = News.objects.filter(category=key, status='published').count()
        cats.append({'slug': key, 'name': info['name'], 'description': info['description'], 'count': count, 'icon': info['icon']})
    return render(request, 'news/categories.html', {'categories': cats})


class CategoryDetailView(ListView):
    model = News
    template_name = 'news/category_detail.html'
    context_object_name = 'news_list'
    paginate_by = 6

    def get_queryset(self):
        return News.objects.filter(category=self.kwargs['category'], status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category']
        info = CATEGORY_INFO.get(category_slug, {'name': category_slug, 'description': ''})
        context['category'] = {'slug': category_slug, 'name': info['name'], 'description': info['description']}
        return context


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
    if request.method != 'POST':
        return redirect('news:news_detail', slug=slug)
    if not request.user.is_authenticated:
        return redirect('news:login')
    news = get_object_or_404(News, slug=slug)
    SavedNews.objects.get_or_create(user=request.user, news=news)
    return redirect('news:news_detail', slug=slug)


def unsave_news(request, slug):
    if request.method != 'POST':
        return redirect('news:news_detail', slug=slug)
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


class NewsUpdateView(SuccessMessageMixin, UpdateView):
    model = News
    template_name = 'news/edit_news.html'
    form_class = NewsForm
    success_message = 'Новость обновлена!'

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'slug': self.object.slug})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('news:login')
        self.object = self.get_object()
        if self.object.author != request.user:
            messages.error(request, 'Вы не можете редактировать эту новость.')
            return redirect('news:news_detail', slug=self.object.slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        news = form.save(commit=False)
        if not news.slug:
            news.slug = slugify(news.title) or f'news-{int(time.time())}'
            base_slug = news.slug
            counter = 1
            while News.objects.filter(slug=news.slug).exclude(pk=news.pk).exists():
                news.slug = f"{base_slug}-{counter}"
                counter += 1
        if news.status == 'rejected':
            news.status = 'pending'
            news.rejection_reason = ''
        news.save()
        return super().form_valid(form)


class NewsDeleteView(SuccessMessageMixin, DeleteView):
    model = News
    success_url = reverse_lazy('news:profile')
    success_message = 'Новость удалена!'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('news:login')
        self.object = self.get_object()
        if self.object.author != request.user:
            messages.error(request, 'Вы не можете удалить эту новость.')
            return redirect('news:news_detail', slug=self.object.slug)
        return super().dispatch(request, *args, **kwargs)


def add_comment(request, slug):
    if request.method != 'POST':
        return redirect('news:news_detail', slug=slug)
    if not request.user.is_authenticated:
        return redirect('news:login')
    news = get_object_or_404(News, slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.news = news
        comment.author = request.user
        parent_id = form.cleaned_data.get('parent')
        if parent_id:
            try:
                comment.parent = Comment.objects.get(id=parent_id, news=news)
            except Comment.DoesNotExist:
                pass
        comment.save()
    return redirect('news:news_detail', slug=slug)


def delete_comment(request, slug, comment_id):
    if request.method != 'POST':
        return redirect('news:news_detail', slug=slug)
    if not request.user.is_authenticated:
        return redirect('news:login')
    comment = get_object_or_404(Comment, id=comment_id, news__slug=slug)
    if comment.author != request.user:
        messages.error(request, 'Вы не можете удалить этот комментарий.')
        return redirect('news:news_detail', slug=slug)
    comment.delete()
    return redirect('news:news_detail', slug=slug)


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user)
    return render(request, 'news/notifications.html', {'notifications': user_notifications})


@require_POST
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('news:notifications')


@require_POST
@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('news:notifications')


def about(request):
    return render(request, 'pages/about.html')


def contacts(request):
    return render(request, 'pages/contacts.html')


class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy.html'


def subscribe(request):
    if request.method != 'POST':
        return redirect('news:home')
    email = request.POST.get('email', '').strip()
    if not email:
        messages.error(request, 'Укажите email.')
        return redirect('news:home')
    try:
        Subscription.objects.create(email=email)
        messages.success(request, 'Вы подписались на рассылку!')
    except:
        messages.info(request, 'Вы уже подписаны.')
    return redirect('news:home')
