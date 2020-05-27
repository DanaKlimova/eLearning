from django.contrib import admin
from courses.models import Course


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_visible",
        "status",
        "type",
        "owner_type",
        "owner_user",
        "min_pass_grade",
        "rating",
    )
    readonly_fields = (
        "name",
        "status",
        "type",
        "owner_type",
        "owner_user",
        "min_pass_grade",
        "content",
        "students",
        "rating",
        "cover",
    )
    ordering = ("is_visible",)


admin.site.register(Course, CourseAdmin)
