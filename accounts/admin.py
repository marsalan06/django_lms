from django.contrib import admin
from .models import User, Student, Parent, Organization, DepartmentHead
from django.utils.html import format_html


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "get_full_name",
        "username",
        "email",
        "organization",
        "is_active",
        "is_student",
        "is_lecturer",
        "is_parent",
        "is_staff",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "organization",
        "email",
        "is_active",
        "is_lecturer",
        "is_parent",
        "is_staff",
    ]

    class Meta:
        managed = True
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save_model(self, request, obj, form, change):
        obj.save(from_admin=True)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "type_of_org", "establishment_year", "status")
    list_filter = ("type_of_org", "status")
    search_fields = ("name", "type_of_org", "region")
    ordering = ("name", "establishment_year")


admin.site.register(Organization, OrganizationAdmin)

admin.site.register(User, UserAdmin)


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "student_name",
        "program",
        "organization",
        "gender",
        "date_joined",
        "actions_column",
    )
    list_filter = ("level", "program", "student__date_joined")
    search_fields = (
        "student__username",
        "student__first_name",
        "student__last_name",
        "level",
        "program",
    )

    def username(self, obj):
        return obj.student.username

    def student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def organization(self, obj):
        return obj.student.organization

    def date_joined(self, obj):
        return obj.student.date_joined

    def gender(self, obj):
        return obj.student.gender

    def actions_column(self, obj):
        return format_html('<a href="{}">View</a>', obj.get_absolute_url())

    actions_column.short_description = "Actions"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("student", "program")
        return queryset

    def has_delete_permission(self, request, obj=None):
        return False  # You can adjust this as per your requirement


admin.site.register(Student, StudentAdmin)

admin.site.register(Parent)
admin.site.register(DepartmentHead)
