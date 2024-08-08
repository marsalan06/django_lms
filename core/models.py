from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse

NEWS = "News"
EVENTS = "Event"

POST = (
    (NEWS, "News"),
    (EVENTS, "Event"),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

SEMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)


class NewsAndEventsQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(posted_as__icontains=query)
        )
        return self.filter(lookups).distinct()


class NewsAndEventsManager(models.Manager):
    def get_queryset(self):
        return NewsAndEventsQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(
            id=id
        )  # NewsAndEvents.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().search(query)

    def custom_search(self, query=None, organization=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(tags__icontains=query)
            )
            if organization:
                or_lookup &= Q(organization__name__icontains=organization)
            queryset = queryset.filter(or_lookup).distinct()
        return queryset


class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200, null=True)
    summary = models.TextField(max_length=200, blank=True, null=True)
    posted_as = models.CharField(choices=POST, max_length=10)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="organization_news_events",
    )
    tags = models.JSONField(blank=True, null=True)

    objects = NewsAndEventsManager()

    def __str__(self):
        return self.title


class Session(models.Model):
    session = models.CharField(max_length=200, unique=True)
    is_current_session = models.BooleanField(default=False, blank=True, null=True)
    next_session_begins = models.DateField(blank=True, null=True)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="organization_session",
    )

    def save(self, *args, **kwargs):
        if self.is_current_session:
            # Mark all other sessions in the same organization as not current
            Session.objects.filter(organization=self.organization).exclude(
                pk=self.pk
            ).update(is_current_session=False)

            # Mark all semesters in other sessions as not current
            Semester.objects.filter(session__organization=self.organization).exclude(
                session=self
            ).update(is_current_semester=False)

        else:
            # Ensure that no semester is marked as current if the session is not current
            self.semesters.update(is_current_semester=False)

        # Save the current session as the selected one
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session} ({self.organization.name})"


class Semester(models.Model):
    semester = models.CharField(max_length=10, choices=SEMESTER, blank=True)
    is_current_semester = models.BooleanField(default=False, blank=True, null=True)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="semesters",
    )
    next_semester_begins = models.DateField(null=True, blank=True)

    def clean(self):
        if self.session:
            # Ensure no more than 3 semesters exist for the session
            semester_count = (
                Semester.objects.filter(session=self.session)
                .exclude(pk=self.pk)
                .count()
            )
            if semester_count >= 3:
                raise ValidationError("A session can have a maximum of 3 semesters.")

            # Ensure each semester choice (First, Second, Third) is unique within the session
            if (
                Semester.objects.filter(session=self.session, semester=self.semester)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    f"The semester '{self.semester}' is already assigned to this session."
                )

    def save(self, *args, **kwargs):
        # Run the clean method to validate before saving
        self.clean()

        if self.is_current_semester:
            # Check if the associated session is current
            if not self.session.is_current_session:
                raise ValidationError(
                    "Cannot mark this semester as current because its session is not current."
                )

            # Ensure all other semesters in the same session are marked as not current
            Semester.objects.filter(session=self.session).exclude(pk=self.pk).update(
                is_current_semester=False
            )

        # Save the current semester as the selected one
        super().save(*args, **kwargs)

    def __str__(self):
        return self.semester


class ActivityLog(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.created_at}]{self.message}"
