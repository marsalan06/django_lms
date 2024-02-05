from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from PIL import Image
import secrets

from course.models import Program

from .validators import ASCIIUsernameValidator

# LEVEL_COURSE = "Level course"
BACHLOAR_DEGREE = "Bachloar"
MASTER_DEGREE = "Master"

LEVEL = (
    # (LEVEL_COURSE, "Level course"),
    (BACHLOAR_DEGREE, "Bachloar Degree"),
    (MASTER_DEGREE, "Master Degree"),
)

FATHER = "Father"
MOTHER = "Mother"
BROTHER = "Brother"
SISTER = "Sister"
GRAND_MOTHER = "Grand mother"
GRAND_FATHER = "Grand father"
OTHER = "Other"

RELATION_SHIP = (
    (FATHER, "Father"),
    (MOTHER, "Mother"),
    (BROTHER, "Brother"),
    (SISTER, "Sister"),
    (GRAND_MOTHER, "Grand mother"),
    (GRAND_FATHER, "Grand father"),
    (OTHER, "Other"),
)

SCHOOL = "School"
COLLEGE = "College"
UNIVERSITY = "University"
TYPE_OF_ORG = [
    (SCHOOL, "School"),
    (COLLEGE, "College"),
    (UNIVERSITY, "University"),
]

ACTIVE = "Active"
INACTIVE = "Inactive"
STATUS_CHOICES = [
    (ACTIVE, "Active"),
    (INACTIVE, "Inactive"),
]


class CustomUserManager(UserManager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            queryset = queryset.filter(
                or_lookup
            ).distinct()  # distinct() is often necessary with Q lookups
        return queryset


class OrganizationManager(models.Manager):
    def create_with_unique_hex_id(self, **kwargs):
        unique_id = None
        is_unique = False
        while not is_unique:
            unique_id = secrets.token_hex(
                3
            )  # Generates a 3-byte hex string, which is 6 characters long
            is_unique = not self.model.objects.filter(
                organization_id=unique_id
            ).exists()
        kwargs["organization_id"] = unique_id
        return super().create(**kwargs)


class Organization(models.Model):
    organization_id = models.CharField(
        max_length=6, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=255)
    type_of_org = models.CharField(max_length=100, choices=TYPE_OF_ORG)
    address = models.TextField(null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True)
    website = models.URLField(blank=True, null=True)
    establishment_year = models.IntegerField(
        validators=[
            MinValueValidator(
                1000
            ),  # Assuming no organization dates back before the year 1000
            MaxValueValidator(now().year),  # Ensures the year isn't in the future
        ],
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="Active")
    logo = models.ImageField(
        upload_to="organization_logos/%Y/%m/%d/", blank=True, null=True
    )
    domain = models.CharField(
        max_length=255, blank=True, null=True
    )  # Domain field for whitelabeling solutions

    objects = OrganizationManager()

    class Meta:
        db_table = "organizations"

    def __str__(self):
        return f"{self.name}_{self.organization_id}"

    def save(self, *args, **kwargs):
        if not self.pk:  # If the object is new
            self.organization_id = (
                Organization.objects.create_with_unique_hex_id().organization_id
            )
        super(Organization, self).save(*args, **kwargs)


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True
    )
    email = models.EmailField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )

    username_validator = ASCIIUsernameValidator()

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    @classmethod
    def get_student_count(cls):
        return cls.objects.filter(is_student=True).count()

    @classmethod
    def get_lecturer_count(cls):
        return cls.objects.filter(is_lecturer=True).count()

    @classmethod
    def get_superuser_count(cls):
        return cls.objects.filter(is_superuser=True).count()

    def __str__(self):
        return "{} ({})".format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            role = "Admin"
        elif self.is_student:
            role = "Student"
        elif self.is_lecturer:
            role = "Lecturer"
        elif self.is_parent:
            role = "Parent"

        return role

    @property
    def get_user_org(self):
        if self.organization:
            return self.organization.name
        else:
            return None

    @property
    def get_org_logo(self):
        if self.organization:
            return self.organization
        else:
            return None

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + "default.png"
            return no_picture

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + "default.png":
            self.picture.delete()
        super().delete(*args, **kwargs)


class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = Q(level__icontains=query) | Q(program__icontains=query)
            qs = qs.filter(
                or_lookup
            ).distinct()  # distinct() is often necessary with Q lookups
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    # id_number = models.CharField(max_length=20, unique=True, blank=True)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    objects = StudentManager()

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self):
        # return self.student.get_full_name
        return self.student.username

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)


class Parent(models.Model):
    """
    Connect student with their parent, parents can
    only view their connected students information
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # What is the relationship between the student and
    # the parent (i.e. father, mother, brother, sister)
    relation_ship = models.TextField(choices=RELATION_SHIP, blank=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return self.user.username


class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return "{}".format(self.user)
