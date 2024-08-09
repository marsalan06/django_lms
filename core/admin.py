from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.html import format_html


from .models import Session, Semester, NewsAndEvents


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "organization",
        "is_current_session",
        "next_session_begins",
    )
    list_filter = ("organization", "is_current_session")
    search_fields = ("session", "organization__name")
    ordering = ("organization", "session")
    list_editable = ("is_current_session", "next_session_begins")
    actions = ["make_current_session"]

    def make_current_session(self, request, queryset):
        for session in queryset:
            # Set all other sessions of the same organization as not current
            Session.objects.filter(organization=session.organization).exclude(
                pk=session.pk
            ).update(is_current_session=False)

            # Set all semesters in other sessions as not current
            Semester.objects.filter(session__organization=session.organization).exclude(
                session=session
            ).update(is_current_semester=False)

            # Set the selected session as current
            session.is_current_session = True
            session.save()

        self.message_user(
            request,
            "Selected session has been marked as current and others have been updated.",
        )

    make_current_session.short_description = "Mark selected session as current"


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = (
        "semester",
        "session",
        "is_current_semester",
        "next_semester_begins",
    )
    list_filter = ("session__organization", "is_current_semester")
    search_fields = ("semester", "session__session", "session__organization__name")
    ordering = ("session__organization", "session", "semester")
    list_editable = ("is_current_semester", "next_semester_begins")
    actions = ["make_current_semester"]

    def save_model(self, request, obj, form, change):
        try:
            # Save the semester
            obj.save()
            self.message_user(request, "Semester saved successfully.", level="success")
        except ValidationError as e:
            self.message_user(
                request, format_html("<br>".join(e.messages)), level="error"
            )

    def make_current_semester(self, request, queryset):
        for semester in queryset:
            if semester.is_current_semester:
                # Check if the associated session is current
                if not semester.session.is_current_session:
                    self.message_user(
                        request,
                        f"Cannot mark semester '{semester.semester}' as current because its session is not current.",
                        level="error",
                    )
                    continue

                # Set all other semesters in the same session as not current
                Semester.objects.filter(session=semester.session).exclude(
                    pk=semester.pk
                ).update(is_current_semester=False)

                # Set the selected semester as current
                semester.is_current_semester = True
                semester.save()

        self.message_user(
            request,
            "Selected semester(s) have been marked as current and others have been updated.",
        )

    make_current_semester.short_description = "Mark selected semester as current"


admin.site.register(NewsAndEvents)
