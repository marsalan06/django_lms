from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django import forms
from django.db import transaction
from django.utils.timezone import now

from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.auth.forms import PasswordResetForm
from course.models import Program
from .models import (
    User,
    Student,
    Parent,
    Organization,
    RELATION_SHIP,
    LEVEL,
    TYPE_OF_ORG,
    STATUS_CHOICES,
)
from .models import User, Student, Parent, RELATION_SHIP, LEVEL, GENDERS


class StaffAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Username",
        required=False,
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )

    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )

    email = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Email",
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
        required=False,
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
        required=False,
    )

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(), required=False, label="Organization"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        # Dynamically filter `organization` field based on request.user

        user_organization = user.organization
        if user_organization:
            self.fields["organization"].queryset = Organization.objects.filter(
                organization_id=user_organization.organization_id
            )
        else:
            # Fallback to default behavior if user is not provided or has no specific organization
            self.fields["organization"].queryset = Organization.objects.all()

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")
        if self.cleaned_data["organization"]:
            user.organization = self.cleaned_data["organization"]

        # Generate a username
        registration_date = datetime.now().strftime("%Y")
        total_lecturers_count = User.objects.filter(is_lecturer=True).count()
        generated_username = (
            f"{settings.LECTURER_ID_PREFIX}-{registration_date}-{total_lecturers_count}"
        )
        # Generate a password
        generated_password = User.objects.make_random_password()

        user.username = generated_username
        user.set_password(generated_password)

        if commit:
            user.save()
            print("-------user name-----: ", generated_username)
            print("-------password------: ", generated_password)
            # # Send email with the generated credentials
            # send_mail(
            #     "Your Django LMS account credentials",
            #     f"Your username: {generated_username}\nYour password: {generated_password}",
            #     "from@example.com",
            #     [user.email],
            #     fail_silently=False,
            # )

        return user


class OrganizationAddForm(forms.ModelForm):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Organization Name"}
        ),
        label="Name",
    )
    type_of_org = forms.ChoiceField(
        choices=TYPE_OF_ORG,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Type of Organization",
    )
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Address"}
        ),
        label="Address",
        required=False,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
        label="Email",
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        ),
        label="Phone Number",
        required=False,
    )
    website = forms.URLField(
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "Website"}
        ),
        label="Website",
        required=False,
    )
    establishment_year = forms.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(now().year)],
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Establishment Year"}
        ),
        label="Establishment Year",
        required=False,
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Status",
    )
    domain = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Domain"}
        ),
        label="Domain",
        required=False,
    )
    logo = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="Logo",
        required=False,
    )

    class Meta:
        model = Organization
        fields = [
            "name",
            "type_of_org",
            "address",
            "email",
            "phone_number",
            "website",
            "establishment_year",
            "status",
            "domain",
            "logo",
        ]


class StudentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"type": "text", "class": "form-control", "id": "username_id"}
        ),
        label="Username",
        required=False,
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    # level = forms.CharField(
    #     widget=forms.Select(
    #         choices=LEVEL,
    #         attrs={
    #             "class": "browser-default custom-select form-control",
    #         },
    #     ),
    # )

    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Program",
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
        required=False,
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
        required=False,
    )

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(), required=False, label="Organization"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        # Dynamically filter `organization` field based on request.user

        user_organization = user.organization
        if user_organization:
            self.fields["organization"].queryset = Organization.objects.filter(
                organization_id=user_organization.organization_id
            )
        else:
            # Fallback to default behavior if user is not provided or has no specific organization
            self.fields["organization"].queryset = Organization.objects.all()

    # def validate_email(self):
    #     email = self.cleaned_data['email']
    #     if User.objects.filter(email__iexact=email, is_active=True).exists():
    #         raise forms.ValidationError("Email has taken, try another email address. ")

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")
        if self.cleaned_data["organization"]:
            user.organization = self.cleaned_data["organization"]
        # Generate a username based on first and last name and registration date
        registration_date = datetime.now().strftime("%Y")
        total_students_count = Student.objects.count()
        generated_username = (
            f"{settings.STUDENT_ID_PREFIX}-{registration_date}-{total_students_count}"
        )
        # Generate a password
        generated_password = User.objects.make_random_password()

        user.username = generated_username
        user.set_password(generated_password)

        if commit:
            user.save()
            Student.objects.create(
                student=user,
                level=self.cleaned_data.get("level"),
                program=self.cleaned_data.get("program"),
            )

            # Send email with the generated credentials
            # send_mail(
            #     "Your Django LMS account credentials",
            #     f"Your ID: {generated_username}\nYour password: {generated_password}",
            #     settings.EMAIL_FROM_ADDRESS,
            #     [user.email],
            #     fail_silently=False,
            # )
        print("--------user----password----: ", user.username, generated_password)

        return user


class ProfileUpdateForm(UserChangeForm):

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Phone No.",
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address / city",
    )
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(), required=False, label="Organization"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        # Dynamically filter `organization` field based on request.user

        user_organization = user.organization
        if user_organization:
            self.fields["organization"].queryset = Organization.objects.filter(
                organization_id=user_organization.organization_id
            )
        else:
            # Fallback to default behavior if user is not provided or has no specific organization
            self.fields["organization"].queryset = Organization.objects.all()

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone",
            "address",
            "picture",
            "organization",
        ]


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-mail address. "
            self.add_error("email", msg)
            return email


class ParentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Username",
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Student",
    )

    relation_ship = forms.CharField(
        widget=forms.Select(
            choices=RELATION_SHIP,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
    )

    # def validate_email(self):
    #     email = self.cleaned_data['email']
    #     if User.objects.filter(email__iexact=email, is_active=True).exists():
    #         raise forms.ValidationError("Email has taken, try another email address. ")

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        user.save()
        parent = Parent.objects.create(
            user=user,
            student=self.cleaned_data.get("student"),
            relation_ship=self.cleaned_data.get("relation_ship"),
        )
        parent.save()
        return user
