from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail, get_connection
from django.conf import settings
from .models import News, Notification, Subscription


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

    connection = get_connection(timeout=5)

    if instance.status == 'published':
        Notification.objects.create(
            user=instance.author,
            news=instance,
            message=f'Ваша новость «{instance.title}» опубликована!'
        )
        if instance.author.email:
            try:
                send_mail(
                    subject='Новость опубликована — ResonateNews',
                    message=f'Здравствуйте, {instance.author.username}!\n\n'
                            f'Ваша новость «{instance.title}» опубликована на сайте ResonateNews.\n'
                            f'Читать: http://localhost:8000/news/{instance.slug}/\n\n'
                            f'Спасибо за ваш вклад!\n--\nResonateNews',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.author.email],
                    connection=connection,
                    fail_silently=True,
                )
            except Exception:
                pass

        subscriber_emails = Subscription.objects.values_list('email', flat=True)
        if subscriber_emails:
            try:
                send_mail(
                    subject=f'Новая новость: {instance.title} — ResonateNews',
                    message=f'Здравствуйте!\n\n'
                            f'На сайте ResonateNews опубликована новая новость:\n'
                            f'«{instance.title}»\n\n'
                            f'{instance.excerpt}\n\n'
                            f'Читать полностью: http://localhost:8000/news/{instance.slug}/\n\n'
                            f'--\nResonateNews',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(subscriber_emails),
                    connection=connection,
                    fail_silently=True,
                )
            except Exception:
                pass

    elif instance.status == 'rejected':
        reason = instance.rejection_reason or 'Не указана'
        Notification.objects.create(
            user=instance.author,
            news=instance,
            message=f'Ваша новость «{instance.title}» отклонена. Причина: {reason}'
        )
        if instance.author.email:
            try:
                send_mail(
                    subject='Новость отклонена — ResonateNews',
                    message=f'Здравствуйте, {instance.author.username}!\n\n'
                            f'Ваша новость «{instance.title}» отклонена модератором.\n'
                            f'Причина: {reason}\n\n'
                            f'Вы можете отредактировать новость и отправить её снова:\n'
                            f'http://localhost:8000/news/{instance.slug}/edit/\n\n'
                            f'--\nResonateNews',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.author.email],
                    connection=connection,
                    fail_silently=True,
                )
            except Exception:
                pass
