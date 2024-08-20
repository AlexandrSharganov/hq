from django.contrib.auth.models import AbstractUser
from django.db import models

from courses.models import Course, Group

class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    """Модель баланса пользователя."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='Пользователь'
    )
    bonus_value = models.PositiveIntegerField(
        default=1000
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'

    def __str__(self):
        return f'{self.user} {self.bonus_value}'


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="customers"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="students"
    )
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_string'
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.course}'
