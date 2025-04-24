from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "is_active", "dob")
    list_filter = ("is_active", "is_staff", "dob")
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (  # new fieldset added on to the bottom
            # group heading of your choice; set to None for a blank space instead of a header
            "User Details",
            {
                "fields": (
                    "dob",
                    "is_profile_setup",
                ),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, CustomUserAdmin)
