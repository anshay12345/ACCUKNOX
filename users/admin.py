from django.contrib import admin
from .models import User, UserManager, FriendRequest
# Register your models here.

admin.site.register(User)
admin.site.register(FriendRequest)

