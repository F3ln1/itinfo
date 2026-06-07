from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import News, SavedNews, Category, Notification


class NewsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )
        self.news = News.objects.create(
            title='Test News Title',
            slug='test-news-title',
            content='Test content for news article',
            excerpt='Short excerpt',
            category='it',
            author=self.user,
            status='published',
        )

    def test_news_creation(self):
        self.assertEqual(News.objects.count(), 1)
        self.assertEqual(str(self.news), 'Test News Title')

    def test_news_is_published_property(self):
        self.assertTrue(self.news.is_published)
        self.news.status = 'pending'
        self.assertFalse(self.news.is_published)

    def test_news_default_status(self):
        news2 = News.objects.create(
            title='Pending News',
            slug='pending-news',
            content='Content',
            excerpt='Excerpt',
            category='science',
            author=self.user,
        )
        self.assertEqual(news2.status, 'pending')

    def test_get_category_tag_class(self):
        self.assertEqual(self.news.get_category_tag_class(), 'news_tag--it')
        news_science = News.objects.create(
            title='Science News',
            slug='science-news',
            content='Content',
            excerpt='Excerpt',
            category='science',
            author=self.user,
            status='published',
        )
        self.assertEqual(news_science.get_category_tag_class(), 'news_tag--science')
        news_tech = News.objects.create(
            title='Tech News',
            slug='tech-news',
            content='Content',
            excerpt='Excerpt',
            category='tech',
            author=self.user,
            status='published',
        )
        self.assertEqual(news_tech.get_category_tag_class(), 'news_tag--tech')

    def test_get_category_display_ru(self):
        self.assertEqual(self.news.get_category_display_ru(), 'IT-технологии')

    def test_news_ordering(self):
        news2 = News.objects.create(
            title='Second News',
            slug='second-news',
            content='Content',
            excerpt='Excerpt',
            category='science',
            author=self.user,
            status='published',
        )
        queryset = News.objects.all()
        self.assertEqual(queryset.first(), news2)

    def test_saved_news_unique_together(self):
        SavedNews.objects.create(user=self.user, news=self.news)
        with self.assertRaises(Exception):
            SavedNews.objects.create(user=self.user, news=self.news)

    def test_saved_news_str(self):
        saved = SavedNews.objects.create(user=self.user, news=self.news)
        self.assertEqual(str(saved), 'testuser - Test News Title')

    def test_category_model(self):
        cat = Category.objects.create(name='IT', slug='it')
        self.assertEqual(str(cat), 'IT')


class HomePageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author', password='pass1234'
        )
        for i in range(8):
            News.objects.create(
                title=f'Published News {i}',
                slug=f'published-news-{i}',
                content='Content',
                excerpt='Excerpt',
                category='it' if i % 2 == 0 else 'science',
                author=self.user,
                status='published',
            )
        News.objects.create(
            title='Pending News',
            slug='pending-news',
            content='Content',
            excerpt='Excerpt',
            category='it',
            author=self.user,
            status='pending',
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_shows_only_published_news(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(len(response.context['news_list']), 6)
        for news in response.context['news_list']:
            self.assertEqual(news.status, 'published')

    def test_home_page_has_featured_news(self):
        response = self.client.get(reverse('news:home'))
        self.assertIsNotNone(response.context['featured_news'])
        self.assertEqual(response.context['featured_news'].status, 'published')


class NewsListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author', password='pass1234'
        )
        for i in range(10):
            News.objects.create(
                title=f'News {i}',
                slug=f'news-{i}',
                content='Content',
                excerpt='Excerpt',
                category='it',
                author=self.user,
                status='published',
            )
        News.objects.create(
            title='Science News',
            slug='science-news',
            content='Science content',
            excerpt='Science excerpt',
            category='science',
            author=self.user,
            status='published',
        )
        News.objects.create(
            title='Pending Item',
            slug='pending-item',
            content='Content',
            excerpt='Excerpt',
            category='tech',
            author=self.user,
            status='pending',
        )

    def test_news_list_shows_only_published(self):
        response = self.client.get(reverse('news:news_list'))
        for news in response.context['news_list']:
            self.assertEqual(news.status, 'published')

    def test_news_list_pagination(self):
        response = self.client.get(reverse('news:news_list'))
        self.assertEqual(len(response.context['news_list']), 6)
        self.assertTrue(response.context['is_paginated'])

    def test_news_list_filter_by_category(self):
        response = self.client.get(reverse('news:news_list'), {'category': 'science'})
        for news in response.context['news_list']:
            self.assertEqual(news.category, 'science')

    def test_news_list_filter_by_author(self):
        response = self.client.get(reverse('news:news_list'), {'author': 'author'})
        self.assertEqual(len(response.context['news_list']), 6)

    def test_news_list_filter_by_nonexistent_author_returns_empty(self):
        response = self.client.get(reverse('news:news_list'), {'author': 'nonexistent'})
        self.assertEqual(len(response.context['news_list']), 0)

    def test_news_list_filter_category_and_author(self):
        response = self.client.get(
            reverse('news:news_list'),
            {'category': 'science', 'author': 'author'},
        )
        for news in response.context['news_list']:
            self.assertEqual(news.category, 'science')

    def test_news_list_context_categories(self):
        response = self.client.get(reverse('news:news_list'))
        self.assertEqual(response.context['categories'], ['it', 'science', 'tech'])

    def test_news_list_context_current_category(self):
        response = self.client.get(reverse('news:news_list'), {'category': 'science'})
        self.assertEqual(response.context['current_category'], 'science')

    def test_news_list_context_current_author(self):
        response = self.client.get(reverse('news:news_list'), {'author': 'testuser'})
        self.assertEqual(response.context['current_author'], 'testuser')


class NewsDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author', password='pass1234'
        )
        self.news = News.objects.create(
            title='Detail Test',
            slug='detail-test',
            content='Detailed content',
            excerpt='Excerpt',
            category='it',
            author=self.user,
            status='published',
            views=0,
        )
        for i in range(5):
            News.objects.create(
                title=f'Related News {i}',
                slug=f'related-news-{i}',
                content='Content',
                excerpt='Excerpt',
                category='it',
                author=self.user,
                status='published',
            )

    def test_news_detail_status(self):
        response = self.client.get(
            reverse('news:news_detail', kwargs={'slug': self.news.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_news_detail_increments_views_once(self):
        self.client.get(reverse('news:news_detail', kwargs={'slug': self.news.slug}))
        self.news.refresh_from_db()
        self.assertEqual(self.news.views, 1)
        self.client.get(reverse('news:news_detail', kwargs={'slug': self.news.slug}))
        self.news.refresh_from_db()
        self.assertEqual(self.news.views, 1)

    def test_news_detail_related_news(self):
        response = self.client.get(
            reverse('news:news_detail', kwargs={'slug': self.news.slug})
        )
        self.assertIn('related_news', response.context)
        self.assertEqual(len(response.context['related_news']), 3)

    def test_news_detail_not_found(self):
        response = self.client.get(
            reverse('news:news_detail', kwargs={'slug': 'nonexistent-slug'})
        )
        self.assertEqual(response.status_code, 404)

    def test_news_detail_is_saved_for_authenticated(self):
        self.client.login(username='author', password='pass1234')
        response = self.client.get(
            reverse('news:news_detail', kwargs={'slug': self.news.slug})
        )
        self.assertIn('is_saved', response.context)
        self.assertFalse(response.context['is_saved'])

    def test_news_detail_is_saved_true_when_saved(self):
        self.client.login(username='author', password='pass1234')
        SavedNews.objects.create(user=self.user, news=self.news)
        response = self.client.get(
            reverse('news:news_detail', kwargs={'slug': self.news.slug})
        )
        self.assertTrue(response.context['is_saved'])


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_status(self):
        response = self.client.get(reverse('news:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        response = self.client.post(reverse('news:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertRedirects(response, reverse('news:home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_with_existing_username(self):
        User.objects.create_user(username='existing', password='pass12345')
        response = self.client.post(reverse('news:register'), {
            'username': 'existing',
            'email': 'existing@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', [
            'Пользователь с таким именем уже существует.'
        ])

    def test_register_password_mismatch(self):
        response = self.client.post(reverse('news:register'), {
            'username': 'user123',
            'email': 'user@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)

    def test_register_authenticated_user_redirected(self):
        User.objects.create_user(username='authuser', password='pass12345')
        self.client.login(username='authuser', password='pass12345')
        response = self.client.get(reverse('news:register'))
        self.assertRedirects(response, reverse('news:home'))


class LoginLogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )

    def test_login_page_status(self):
        response = self.client.get(reverse('news:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('news:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('news:home'))

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('news:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(
            response.context['form'].errors.get('__all__')
        )

    def test_login_authenticated_user_redirected(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:login'))
        self.assertRedirects(response, reverse('news:home'))

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:logout'))
        self.assertRedirects(response, reverse('news:home'))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.news_published = News.objects.create(
            title='Published Article',
            slug='published-article',
            content='Content',
            excerpt='Excerpt',
            category='it',
            author=self.user,
            status='published',
        )
        self.news_pending = News.objects.create(
            title='Pending Article',
            slug='pending-article',
            content='Content',
            excerpt='Excerpt',
            category='science',
            author=self.user,
            status='pending',
        )
        self.news_rejected = News.objects.create(
            title='Rejected Article',
            slug='rejected-article',
            content='Content',
            excerpt='Excerpt',
            category='tech',
            author=self.user,
            status='rejected',
        )
        SavedNews.objects.create(user=self.user, news=self.news_published)

    def test_profile_redirects_anonymous(self):
        response = self.client.get(reverse('news:profile'))
        self.assertRedirects(response, reverse('news:login'))

    def test_profile_shows_user_stats(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:profile'))
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(response.context['published_count'], 1)
        self.assertEqual(response.context['rejected_count'], 1)
        self.assertEqual(response.context['saved_count'], 1)

    def test_profile_shows_pending_news(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:profile'))
        self.assertIn(self.news_pending, response.context['pending_news'])
        self.assertNotIn(self.news_published, response.context['pending_news'])

    def test_profile_shows_published_news(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:profile'))
        self.assertIn(self.news_published, response.context['published_news'])

    def test_profile_shows_rejected_news(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:profile'))
        self.assertIn(self.news_rejected, response.context['rejected_news'])

    def test_profile_shows_saved_news(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:profile'))
        self.assertEqual(len(response.context['saved_news']), 1)

    def test_profile_only_shows_own_news(self):
        other_user = User.objects.create_user(
            username='otheruser', password='pass12345'
        )
        News.objects.create(
            title='Other Article',
            slug='other-article',
            content='Content',
            excerpt='Excerpt',
            category='it',
            author=other_user,
            status='published',
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('news:profile'))
        for news in response.context['user_news']:
            self.assertEqual(news.author, self.user)


class CreateNewsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author', password='authorpass123'
        )

    def test_create_news_redirects_anonymous(self):
        response = self.client.get(reverse('news:create_news'))
        self.assertRedirects(response, reverse('news:login'))

    def test_create_news_page_status(self):
        self.client.login(username='author', password='authorpass123')
        response = self.client.get(reverse('news:create_news'))
        self.assertEqual(response.status_code, 200)

    def test_create_news_creates_with_pending_status(self):
        self.client.login(username='author', password='authorpass123')
        response = self.client.post(reverse('news:create_news'), {
            'title': 'New Test Article',
            'content': 'Article content here',
            'excerpt': 'Short excerpt',
            'category': 'it',
        })
        self.assertRedirects(response, reverse('news:profile'))
        news = News.objects.get(title='New Test Article')
        self.assertEqual(news.status, 'pending')
        self.assertEqual(news.author, self.user)

    def test_create_news_auto_generates_slug(self):
        self.client.login(username='author', password='authorpass123')
        self.client.post(reverse('news:create_news'), {
            'title': 'Auto Slug Title',
            'content': 'Content',
            'excerpt': 'Excerpt',
            'category': 'science',
        })
        news = News.objects.get(title='Auto Slug Title')
        self.assertEqual(news.slug, slugify('Auto Slug Title'))

    def test_create_news_handles_duplicate_slug(self):
        News.objects.create(
            title='Duplicate Slug',
            slug='duplicate-slug',
            content='Original',
            excerpt='Excerpt',
            category='it',
            author=self.user,
        )
        self.client.login(username='author', password='authorpass123')
        self.client.post(reverse('news:create_news'), {
            'title': 'Duplicate Slug',
            'content': 'New content',
            'excerpt': 'Excerpt',
            'category': 'tech',
        })
        news = News.objects.get(content='New content')
        self.assertEqual(news.slug, 'duplicate-slug-1')


class SaveUnsaveNewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.news = News.objects.create(
            title='Savable News',
            slug='savable-news',
            content='Content',
            excerpt='Excerpt',
            category='it',
            author=self.user,
            status='published',
        )

    def test_save_news_redirects_anonymous(self):
        response = self.client.post(
            reverse('news:save_news', kwargs={'slug': self.news.slug})
        )
        self.assertRedirects(response, reverse('news:login'))

    def test_unsave_news_redirects_anonymous(self):
        response = self.client.post(
            reverse('news:unsave_news', kwargs={'slug': self.news.slug})
        )
        self.assertRedirects(response, reverse('news:login'))

    def test_save_news_creates_saved_news(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('news:save_news', kwargs={'slug': self.news.slug})
        )
        self.assertRedirects(
            response,
            reverse('news:news_detail', kwargs={'slug': self.news.slug}),
        )
        self.assertTrue(
            SavedNews.objects.filter(user=self.user, news=self.news).exists()
        )

    def test_save_news_does_not_create_duplicates(self):
        self.client.login(username='testuser', password='testpass123')
        SavedNews.objects.create(user=self.user, news=self.news)
        self.client.post(
            reverse('news:save_news', kwargs={'slug': self.news.slug})
        )
        self.assertEqual(
            SavedNews.objects.filter(user=self.user, news=self.news).count(),
            1,
        )

    def test_unsave_news_removes_saved_news(self):
        self.client.login(username='testuser', password='testpass123')
        SavedNews.objects.create(user=self.user, news=self.news)
        self.client.post(
            reverse('news:unsave_news', kwargs={'slug': self.news.slug})
        )
        self.assertFalse(
            SavedNews.objects.filter(user=self.user, news=self.news).exists()
        )


class NewsListViewPaginationAndFilteringTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author', password='pass1234'
        )
        for i in range(14):
            News.objects.create(
                title=f'News {i}',
                slug=f'news-{i}',
                content='Content',
                excerpt='Excerpt',
                category='it' if i % 2 == 0 else 'science',
                author=self.user,
                status='published',
            )

    def test_first_page_has_6_items(self):
        response = self.client.get(reverse('news:news_list'))
        self.assertEqual(len(response.context['news_list']), 6)

    def test_second_page_has_6_items(self):
        response = self.client.get(reverse('news:news_list'), {'page': 2})
        self.assertEqual(len(response.context['news_list']), 6)

    def test_third_page_has_2_items(self):
        response = self.client.get(reverse('news:news_list'), {'page': 3})
        self.assertEqual(len(response.context['news_list']), 2)

    def test_filter_pagination_persists(self):
        response = self.client.get(
            reverse('news:news_list'), {'category': 'science'}
        )
        news_science = News.objects.filter(category='science', status='published')
        self.assertEqual(len(response.context['news_list']), min(6, news_science.count()))


class NotificationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )
        self.news = News.objects.create(
            title='Test News',
            slug='test-news',
            content='Content',
            excerpt='Excerpt',
            category='it',
            author=self.user,
            status='pending',
        )

    def test_notification_created_on_publish(self):
        self.news.status = 'published'
        self.news.save()
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)
        self.assertIn('опубликована', notification.message)

    def test_notification_created_on_reject(self):
        self.news.status = 'rejected'
        self.news.rejection_reason = 'Спам'
        self.news.save()
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)
        self.assertIn('отклонена', notification.message)
        self.assertIn('Спам', notification.message)

    def test_no_notification_on_initial_create(self):
        self.assertEqual(Notification.objects.count(), 0)

    def test_no_notification_when_status_unchanged(self):
        self.news.excerpt = 'Updated'
        self.news.save()
        self.assertEqual(Notification.objects.count(), 0)

    def test_no_notification_without_author(self):
        news2 = News.objects.create(
            title='No Author',
            slug='no-author',
            content='Content',
            excerpt='Excerpt',
            category='science',
            status='pending',
        )
        news2.status = 'published'
        news2.save()
        self.assertEqual(Notification.objects.count(), 0)

    def test_notifications_page_redirects_anonymous(self):
        response = self.client.get(reverse('news:notifications'))
        self.assertRedirects(response, f"{reverse('news:login')}?next={reverse('news:notifications')}")

    def test_notifications_page_shows_notifications(self):
        self.client.login(username='testuser', password='testpass123')
        Notification.objects.create(user=self.user, news=self.news, message='Test notify')
        response = self.client.get(reverse('news:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test notify', response.content.decode())

    def test_mark_notification_read(self):
        self.client.login(username='testuser', password='testpass123')
        notification = Notification.objects.create(user=self.user, news=self.news, message='Test')
        self.client.post(reverse('news:mark_notification_read', kwargs={'notification_id': notification.id}))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_read(self):
        self.client.login(username='testuser', password='testpass123')
        Notification.objects.create(user=self.user, news=self.news, message='First')
        Notification.objects.create(user=self.user, news=self.news, message='Second')
        self.client.post(reverse('news:mark_all_read'))
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_unread_count_in_context(self):
        self.client.login(username='testuser', password='testpass123')
        Notification.objects.create(user=self.user, news=self.news, message='Unread')
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.context.get('unread_notifications_count'), 1)
