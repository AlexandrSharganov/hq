from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Subscription

from .models import Group, Course


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """Распределение нового студента в группу курса."""
    if created:
        course = instance.course
        groups = Group.objects.filter(
            course=course
        ).annotate(
            student_count=Count('students')
        ).order_by('student_count')
        
        if groups.exists():
            smallest_group = groups.first()
            instance.group = smallest_group
            instance.save()

@receiver(post_save, sender=Course)
def create_groups_for_course(sender, instance, created, **kwargs):
    """Создание групп при создании курса."""
    if created:
        for i in range(1, 11):
            Group.objects.create(course=instance, title=f"Группа №{i}")
