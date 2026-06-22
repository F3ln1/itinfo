from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import News, Notification


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

    elif instance.status == 'rejected':
        reason = instance.rejection_reason or 'Не указана'
        Notification.objects.create(
            user=instance.author,
            news=instance,
            message=f'Ваша новость «{instance.title}» отклонена. Причина: {reason}'
        )
