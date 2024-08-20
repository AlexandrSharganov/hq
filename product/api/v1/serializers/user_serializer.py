from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.v1.utils import decrease_bonus_value
from courses.models import Course
from users.models import Balance, Subscription


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    
    course = serializers.PrimaryKeyRelatedField(
        queryset = Course.objects.all()
    )
    user = serializers.CharField(read_only=True, source='user.email')
    
    class Meta:
        model = Subscription
        fields = ('course', 'user')

    def validate(self, attrs):
        course = attrs.get('course', None)
        user = self.context['request'].user
        if not course.access_flag:
            raise serializers.ValidationError(
                "В данный момент курс недоступен."
            )
        if not course.is_accessable():
            raise serializers.ValidationError(
                "На курсе не осталось мест."
            )
        if not course.price <= user.wallet.bonus_value:
            raise serializers.ValidationError(
                "У вас недостаточно бонусов для покупки курса."
            )
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data.get('course', None)
        with transaction.atomic():
            if not decrease_bonus_value(user, course):
                raise serializers.ValidationError(
                    "Не удалось обновить баланс пользователя."
                )
            try:
                purchase = Subscription.objects.create(
                    user=user,
                    course=course
                )      
                return purchase
            except Exception as e:
                raise serializers.ValidationError(
                    f'Ошибка при оформлении подписки: {e}'
                )


class BalanceSerializer(serializers.ModelSerializer):
    """Сериализатор баланса пользователя."""
    
    class Meta:
        model = Balance
        fields = (
            'user',
            'bonus_value'
        )
