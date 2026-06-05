import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itinfo.settings')
django.setup()
from news.models import News, Category, SavedNews
from django.contrib.auth.models import User

print(f'Users: {User.objects.count()}')
print(f'News: {News.objects.count()}')
print(f'Published news: {News.objects.filter(status="published").count()}')
print(f'Categories: {Category.objects.count()}')
if News.objects.exists():
    n = News.objects.first()
    print(f'Sample news: {n.title} (status={n.status}, category={n.category})')
