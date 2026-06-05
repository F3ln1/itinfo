from django.contrib import admin
from .models import News, Category, SavedNews


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
        queryset.update(status='published')

    @admin.action(description='Отклонить')
    def reject_news(self, request, queryset):
        queryset.update(status='rejected', rejection_reason='Отклонено модератором')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SavedNews)
class SavedNewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'news__title')
