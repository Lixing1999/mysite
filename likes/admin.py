from django.contrib import admin

# Register your models here.
from .models import LikeCount


@admin.register(LikeCount)
class LikeCoutAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'object_id', 'liked_num')