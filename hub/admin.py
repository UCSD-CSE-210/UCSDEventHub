from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from hub.models import Event, UserProfile, OrganizationDetails
# Register your models here.

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class OrganizationDetailsInline(admin.StackedInline):
    model = OrganizationDetails
    can_delete = False
    verbose_name_plural = 'Organization Details'
    fk_name = 'organization'

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline, OrganizationDetailsInline, ]

    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.register(Event)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)