from django.contrib import admin
from .models import User, Student, Parent, Organization


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


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "type_of_org", "establishment_year", "status")
    list_filter = ("type_of_org", "status")
    search_fields = ("name", "type_of_org", "region")
    ordering = ("name", "establishment_year")


admin.site.register(Organization, OrganizationAdmin)

admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(Parent)
