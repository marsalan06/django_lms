from django import forms

from accounts.models import User, Organization

from .models import Course, CourseAllocation, Program, Upload, UploadVideo, SEMESTER


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["section"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})
        self.fields["organization"].widget.attrs.update({"class": "form-control"})

        user_organization = user.organization
        if user_organization:
            self.fields["organization"].queryset = Organization.objects.filter(
                organization_id=user_organization.organization_id
            )
        else:
            # Fallback to default behavior if user is not provided or has no specific organization
            self.fields["organization"].queryset = Organization.objects.all()


class CourseAddForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Extract the user from kwargs
        program_pk = kwargs.pop("program_pk", None)

        # instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["code"].widget.attrs.update({"class": "form-control"})
        # self.fields['courseUnit'].widget.attrs.update({'class': 'form-control'})
        # self.fields["credit"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})
        self.fields["max_score"].widget.attrs.update({"class": "form-control"})
        self.fields["program"].widget.attrs.update({"class": "form-control"})
        # self.fields["level"].widget.attrs.update({"class": "form-control"})
        # self.fields["year"].widget.attrs.update({"class": "form-control"})
        # if instance is not None:
        #     self.fields["program"].queryset = Program.objects.filter(
        #         pk=instance.program.pk
        #     )

        self.fields["program"].queryset = Program.objects.filter(pk=program_pk)
        self.fields["semester"] = forms.MultipleChoiceField(
            choices=SEMESTER,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            help_text="Select one or more semesters",
        )

    def clean_semester(self):
        semester = self.cleaned_data.get("semester")
        if not semester:
            return ["First", "Second", "Third"]
        return semester
        # if user and hasattr(user, "organization"):
        #     user_organization = user.organization
        #     # Filter the program queryset based on the user's organization
        #     # Assuming there's a way to relate programs to organizations in your model
        #     self.fields["program"].queryset = Program.objects.filter(
        #         organization=user_organization
        #     )
        # else:
        #     # Fallback to default behavior if user is not provided or has no specific organization
        #     self.fields["program"].queryset = Program.objects.all()


class CourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "browser-default checkbox"}
        ),
        required=True,
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={"class": "browser-default custom-select"}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(CourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields["lecturer"].queryset = User.objects.filter(
            is_lecturer=True, organization=user.organization
        )
        self.fields["courses"].queryset = Course.objects.filter(
            program__organization_id=user.organization
        )


class EditCourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={"class": "browser-default custom-select"}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses"]

    def __init__(self, *args, **kwargs):
        #    user = kwargs.pop('user')
        super(EditCourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields["lecturer"].queryset = User.objects.filter(is_lecturer=True)


# Upload files to specific course
class UploadFormFile(forms.ModelForm):
    class Meta:
        model = Upload
        fields = (
            "title",
            "file",
        )

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop("slug")
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["file"].widget.attrs.update({"class": "form-control"})


# Upload video to specific course
class UploadFormVideo(forms.ModelForm):
    class Meta:
        model = UploadVideo
        fields = ("title", "video", "course", "summary")

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop("slug")
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["video"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})
        self.fields["course"].queryset = Course.objects.filter(slug=slug)
