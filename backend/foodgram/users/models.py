from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

DefaultUser = get_user_model()


class User(DefaultUser):
    class Meta:
        proxy = True
        ordering = ('-date_joined',)
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name=_('Подписчик')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name=_('Автор')
    )
    date_subscribed = models.DateTimeField(
        verbose_name=_('Время подписки'),
        auto_now_add=True
    )

    class Meta:
        db_table = 'subscriptions'
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        ordering = ('date_subscribed',)
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'author'),
                name='unique_follow'
            ),
        ]

    def __str__(self):
        return '%s подписан на %s' % (self.subscriber, self.author)
