from django.db import models

from product.settings import (
    MAX_AMOUNT_OF_GROUP,
    MAX_STUDENTS_IN_GROUP
)


class Course(models.Model):
    """Модель продукта - курса."""
    
    MAX_AMOUNT_OF_STUDENTS = MAX_AMOUNT_OF_GROUP * MAX_STUDENTS_IN_GROUP

    author = models.CharField(
        max_length=250,
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )
    access_flag = models.BooleanField(
        default=True
    )
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)
        
    def amount_students(self):
        """Возвращает число зачисленных на курс студентов."""
        return self.customers.count()
    
    def is_accessable(self):
        """Возвращает True если на курсе еще есть места."""
        return self.amount_students() < self.MAX_AMOUNT_OF_STUDENTS

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='курс'
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='groups'
    )
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)
