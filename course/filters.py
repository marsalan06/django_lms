from django.db.models import Q
import django_filters
from .models import Program, CourseAllocation, Course


class ProgramFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label="")
    section = django_filters.CharFilter(
        lookup_expr="exact", label=""
    )  # Added section filter
    organization = django_filters.CharFilter(method="org_filter")

    class Meta:
        model = Program
        fields = ["title", "section"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change html classes and placeholders
        self.filters["title"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Program name"}
        )
        self.filters["section"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Section"}
        )

    @property
    def qs(self):
        parent = super().qs
        if self.request and not self.request.user.is_staff:
            return parent.filter(organization=self.request.user.organization)
        return parent


class CourseAllocationFilter(django_filters.FilterSet):
    lecturer = django_filters.CharFilter(method="filter_by_lecturer", label="")
    course = django_filters.filters.CharFilter(method="filter_by_course", label="")

    class Meta:
        model = CourseAllocation
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change html classes and placeholders
        self.filters["lecturer"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Lecturer"}
        )
        self.filters["course"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Course"}
        )

    def filter_by_lecturer(self, queryset, name, value):
        return queryset.filter(
            Q(lecturer__first_name__icontains=value)
            | Q(lecturer__last_name__icontains=value)
        )

    def filter_by_course(self, queryset, name, value):
        return queryset.filter(courses__title__icontains=value)
