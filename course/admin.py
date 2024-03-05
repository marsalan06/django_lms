from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Program, Course, CourseAllocation, Upload, UploadVideo


class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "organization", "summary_short")
    list_filter = ("organization", "title")
    search_fields = ("title", "organization__name")

    def summary_short(self, obj):
        return obj.summary[:50] + "..." if obj.summary else "No Summary"

    summary_short.short_description = "Summary"

    def get_queryset(self, request):
        qs = super(ProgramAdmin, self).get_queryset(request)
        # Check if user is associated with an organization and filter the queryset accordingly
        if request.user.organization is not None:
            return qs.filter(organization=request.user.organization)
        return qs


admin.site.register(Program, ProgramAdmin)
admin.site.register(Course)
admin.site.register(CourseAllocation)


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "file", "updated_date", "upload_time")
    list_filter = ("course", "updated_date", "upload_time")
    search_fields = (
        "title",
        "course__name",
    )  # Assuming Course model has a 'name' field
    date_hierarchy = "upload_time"


@admin.register(UploadVideo)
class UploadVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "video", "timestamp", "summary")
    list_filter = ("course", "timestamp")
    search_fields = (
        "title",
        "course__name",
        "summary",
    )  # Assuming Course model has a 'name' field
    date_hierarchy = "timestamp"
    prepopulated_fields = {"slug": ("title",)}
