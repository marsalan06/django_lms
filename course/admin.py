from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Program, Course, CourseAllocation, Upload


class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "summary_short")
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
admin.site.register(Upload)
