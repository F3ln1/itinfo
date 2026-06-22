import threading
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import close_old_connections
from .models import News, Notification, Subscription


def send_mail_async(subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,
        )
    except Exception:
        pass
    finally:
        close_old_connections()


@receiver(pre_save, sender=News)
def notify_status_change(sender, instance, **kwargs):
    if instance.pk is None:
        return

    if not instance.author:
        return

    try:
        old = News.objects.get(pk=instance.pk)
    except News.DoesNotExist:
        return

    if old.status == instance.status:
        return

    if instance.status == 'published':
        Notification.objects.create(
            user=instance.author,
            news=instance,
            message=f'Ваша новость «{instance.title}» опубликована!'
        )

        if instance.author.email:
            threading.Thread(target=send_mail_async, args=(
                'Новость опубликована — ResonateNews',
                f'Здравствуйте, {instance.author.username}!\n\n'
                f'Ваша новость «{instance.title}» опубликована на сайте ResonateNews.\n'
                f'Читать: http://localhost:8000/news/{instance.slug}/\n\n'
                f'Спасибо за ваш вклад!\n--\nResonateNews',
                [instance.author.email],
            )).start()

        subscriber_emails = list(Subscription.objects.values_list('email', flat=True))
        if subscriber_emails:
            threading.Thread(target=send_mail_async, args=(
                f'Новая новость: {instance.title} — ResonateNews',
                f'Здравствуйте!\n\n'
                f'На сайте ResonateNews опубликована новая новость:\n'
                f'«{instance.title}»\n\n'
                f'{instance.excerpt}\n\n'
                f'Читать полностью: http://localhost:8000/news/{instance.slug}/\n\n'
                f'--\nResonateNews',
                subscriber_emails,
            )).start()

    elif instance.status == 'rejected':
        reason = instance.rejection_reason or 'Не указана'
        Notification.objects.create(
            user=instance.author,
            news=instance,
            message=f'Ваша новость «{instance.title}» отклонена. Причина: {reason}'
        )

        if instance.author.email:
            threading.Thread(target=send_mail_async, args=(
                'Новость отклонена — ResonateNews',
                f'Здравствуйте, {instance.author.username}!\n\n'
                f'Ваша новость «{instance.title}» отклонена модератором.\n'
                f'Причина: {reason}\n\n'
                f'Вы можете отредактировать новость и отправить её снова:\n'
                f'http://localhost:8000/news/{instance.slug}/edit/\n\n'
                f'--\nResonateNews',
                [instance.author.email],
            )).start()
