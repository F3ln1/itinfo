from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name


class News(models.Model):
    CATEGORY_CHOICES = [
        ('it', 'IT-технологии'),
        ('science', 'Наука'),
        ('tech', 'Техника'),
    ]

    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    ]

    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(verbose_name='Содержание')
    excerpt = models.CharField(max_length=300, verbose_name='Краткое описание')
    image = models.ImageField(upload_to='news/', verbose_name='Изображение', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='news', verbose_name='Автор')
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    rejection_reason = models.TextField(blank=True, verbose_name='Причина отклонения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_category_tag_class(self):
        classes = {
            'it': 'news_tag--it',
            'science': 'news_tag--science',
            'tech': 'news_tag--tech',
        }
        return classes.get(self.category, 'news_tag--it')
    
    def get_category_display_ru(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    @property
    def is_published(self):
        return self.status == 'published'


class SavedNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_news')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'news')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.news.title}"
