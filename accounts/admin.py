from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username',
                    'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, user_object):
        try:
            return format_html(f'<img src="{user_object.profile_picture.url}" '
                               f'width="30" style="border-radius: 50%;">')
        except:
            pass

    thumbnail.short_description = 'Profile Picture'
    list_display = ['thumbnail', 'user', 'city', 'state', 'country']
    list_display_links = ['thumbnail', 'user']


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
