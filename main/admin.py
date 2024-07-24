from django.contrib import admin
from .views.admin_view import admin_site

from .models import User, Post, BlacklistedToken, OTP

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('first_name', 'last_name', 'joining_date')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('avatar_url', 'avatar_id', 'password', 'user_permissions')

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')

admin_site.register(User, UserAdmin)
admin_site.register(Post, PostAdmin)
admin_site.register(BlacklistedToken)
admin_site.register(OTP)

