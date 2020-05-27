from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account, Organization


class AccountAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "is_admin", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ()
    ordering = ("email",)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "employees",
        "is_visible",
    )
    readonly_fields = (
        "name",
        "employees",
    )
    ordering = ("is_visible",)


admin.site.register(Account, AccountAdmin)
admin.site.register(Organization, OrganizationAdmin)
