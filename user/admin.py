from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from user import models


class UserAdmin(BaseUserAdmin):
    """
    Define the admin pages for users.
    """
    ordering = ['id']  # To order the elements by their id fields
    list_display = ['email', 'name']  # To show only the email and name fields.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # classes refers to the css class
            'fields': (
                'email',
                'phone_number',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
                'user_type'
            )
        }),
    )


# Register your models here.
admin.site.register(models.Account, UserAdmin)  # If you not fill the second parameter then django will load the default


# class StudentModelAdmin(admin.ModelAdmin):
#     @csrf_protect
#     def changelist_view(self, request, extra_context=None):
#         if not has_approval_permission(request):
#             self.list_display = []
