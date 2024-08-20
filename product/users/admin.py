from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Balance, Subscription

User = get_user_model()


admin.site.register(User)
admin.site.register(Balance)
admin.site.register(Subscription)



