from django.db.models import Count
from rest_framework import serializers


def decrease_bonus_value(user, course):
    """Функция списания бонусов с баланса."""
    balance = user.wallet
    payment = course.price

    try:
        if balance.bonus_value < payment:
            raise serializers.ValidationError("У вас недостаточно бонусов для покупки курса.")
        balance.bonus_value -= payment
        balance.save()
        return True

    except serializers.ValidationError as e:
        print(f"Ошибка валидации при списании баланса: {e}")
        return False

    except Exception as e:
        print(f"Неожиданная ошибка при списании баланса: {e}")
        return False
