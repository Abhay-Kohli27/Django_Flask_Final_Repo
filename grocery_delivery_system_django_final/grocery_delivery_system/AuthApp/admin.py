from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser

# Register your models here.
class AppUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AppUser._meta.fields]
    search_fields = [field.name for field in AppUser._meta.fields if field.get_internal_type() in ['CharField', 'EmailField', 'TextField']]
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']


    model = AppUser
    ordering = ('email',)


    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
        'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),


    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'address', 'password1', 'password2'),
        }),
    )


admin.site.register(AppUser, AppUserAdmin)
