from django.contrib import admin
from .models import News, Category, SavedNews, Comment, Subscription, Notification


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'views', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'content', 'author')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status',)
    actions = ['publish_news', 'reject_news']

    @admin.action(description='Опубликовать')
    def publish_news(self, request, queryset):
        for news in queryset:
            news.status = 'published'
            news.save()

    @admin.action(description='Отклонить')
    def reject_news(self, request, queryset):
        for news in queryset:
            news.status = 'rejected'
            news.rejection_reason = 'Отклонено модератором'
            news.save()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SavedNews)
class SavedNewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'news__title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'news', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'news__title', 'text')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email',)
