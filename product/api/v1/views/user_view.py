from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers.user_serializer import CustomUserSerializer, BalanceSerializer
from users.models import Balance

User = get_user_model()


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer
#     http_method_names = ["get", "head", "options"]
#     permission_classes = (permissions.IsAdminUser,)


class BalanceViewSet(viewsets.GenericViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = (permissions.IsAdminUser,)

    @action(
        detail=False,
        methods=['put'],
        url_path='update_balance'
    )
    def update_balance(self, request):
        user_id = request.data.get('user')
        user = get_object_or_404(User, id=user_id)
        balance = user.wallet
        serializer = self.get_serializer(
            balance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
