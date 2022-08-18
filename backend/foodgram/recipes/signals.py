from pathlib import Path

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from .models import Recipe


@receiver(post_delete, sender=Recipe, dispatch_uid='delete_media_after_model')
def delete_media(sender, instance, **kwargs):
    if instance.image:
        if Path(instance.image.path).is_file():
            Path(instance.image.path).unlink()


@receiver(pre_save, sender=Recipe)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_file = Recipe.objects.get(pk=instance.pk).image
    except Recipe.DoesNotExist:
        return

    if not old_file == instance.image:
        if Path(old_file.path).is_file():
            Path(old_file.path).unlink()
