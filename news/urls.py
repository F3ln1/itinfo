from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import PasswordChangeCustomForm, PasswordResetCustomForm, SetPasswordCustomForm

app_name = 'news'

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('news/<slug:slug>/save/', views.save_news, name='save_news'),
    path('news/<slug:slug>/unsave/', views.unsave_news, name='unsave_news'),
    path('news/<slug:slug>/edit/', views.NewsUpdateView.as_view(), name='edit_news'),
    path('news/<slug:slug>/delete/', views.NewsDeleteView.as_view(), name='delete_news'),
    path('news/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('news/<slug:slug>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('categories/', views.categories, name='categories'),
    path('category/<slug:category>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('create/', views.CreateNewsView.as_view(), name='create_news'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url=reverse_lazy('news:password_change_done'),
        form_class=PasswordChangeCustomForm,
    ), name='password_change'),
    path('profile/password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html',
    ), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        success_url=reverse_lazy('news:password_reset_done'),
        extra_email_context={'domain': 'localhost:8000', 'protocol': 'http'},
        form_class=PasswordResetCustomForm,
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('news:password_reset_complete'),
        form_class=SetPasswordCustomForm,
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
]
