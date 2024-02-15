from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView
from django_filters.views import FilterView

from core.models import Semester, Session
from course.models import Course
from result.models import TakenCourse

from .decorators import admin_required
from .filters import LecturerFilter, StudentFilter, OrganizationFilter
from .forms import (
    ParentAddForm,
    ProfileUpdateForm,
    StaffAddForm,
    StudentAddForm,
    OrganizationAddForm,
)
from .models import Parent, Student, User, Organization


def validate_username(request):
    username = request.GET.get("username", None)
    data = {"is_taken": User.objects.filter(username__iexact=username).exists()}
    return JsonResponse(data)


def register(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect("login")  # Redirect after POST
        else:
            for error in form.errors:
                messages.error(request, form.errors[error])
    else:
        form = StudentAddForm()  # Empty form for GET request

    return render(request, "registration/register.html", {"form": form})


def register_parent(request):
    if request.method == "POST":
        form = ParentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Parent account created successfully.")
            return redirect("login")  # Redirect after POST
        else:
            for error in form.errors:
                messages.error(request, form.errors[error])
    else:
        form = ParentAddForm()  # Empty form for GET request

    return render(request, "registration/register_parent.html", {"form": form})


@login_required
def profile(request):
    """Show profile of any user that fire out the request"""
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    user_organization = request.user.organization

    if request.user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id
        ).filter(semester=current_semester)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "courses": courses,
                "current_session": current_session,
                "current_semester": current_semester,
                "user_organization": user_organization,
            },
        )
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        try:
            parent = Parent.objects.get(student=level)
        except:
            parent = "no parent set"
        courses = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=level.level
        )
        context = {
            "title": request.user.get_full_name,
            "parent": parent,
            "courses": courses,
            "level": level,
            "current_session": current_session,
            "current_semester": current_semester,
            "user_organization": user_organization,
        }
        return render(request, "accounts/profile.html", context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "staff": staff,
                "current_session": current_session,
                "current_semester": current_semester,
                "user_organization": user_organization,
            },
        )


@login_required
@admin_required
def profile_single(request, id):
    """Show profile of any selected user"""
    if request.user.id == id:
        return redirect("/profile/")

    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(
            semester=current_semester
        )
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "Lecturer",
            "courses": courses,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile_single.html", context)
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = TakenCourse.objects.filter(
            student__student__id=id, course__level=student.level
        )
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "student",
            "courses": courses,
            "student": student,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile_single.html", context)
    else:
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "superuser",
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile_single.html", context)


@login_required
@admin_required
def admin_panel(request):
    return render(
        request, "setting/admin_panel.html", {"title": request.user.get_full_name}
    )


# ########################################################


# ########################################################
# Setting views
# ########################################################
@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(
        request,
        "setting/profile_info_change.html",
        {
            "title": "Setting",
            "form": form,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below. ")
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        "setting/password_change.html",
        {
            "form": form,
        },
    )


# ########################################################


@login_required
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = StaffAddForm(request.POST, user=request.user)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account for lecturer "
                + first_name
                + " "
                + last_name
                + " has been created.",
            )
            return redirect("lecturer_list")
    else:
        form = StaffAddForm(user=request.user)

    context = {
        "title": "Lecturer Add",
        "form": form,
    }

    return render(request, "accounts/add_staff.html", context)


@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=instance, user=request.user
        )
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, "Lecturer " + full_name + " has been updated.")
            return redirect("lecturer_list")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=instance, user=request.user)
    return render(
        request,
        "accounts/edit_lecturer.html",
        {
            "title": "Edit Lecturer",
            "form": form,
        },
    )


@method_decorator([login_required, admin_required], name="dispatch")
class OrganizationListView(FilterView):
    filterset_class = OrganizationFilter
    template_name = "accounts/organization_list.html"  # Adjust the path as needed
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Organizations"
        return context


@method_decorator([login_required, admin_required], name="dispatch")
class LecturerFilterView(FilterView):
    filterset_class = LecturerFilter
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        # Get the base queryset with the is_lecturer condition
        queryset = User.objects.filter(is_lecturer=True)

        # Filter by the organization of the request.user, if available
        user_organization = getattr(self.request.user, "organization", None)
        if user_organization:
            queryset = queryset.filter(organization=user_organization)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lecturers"
        return context


# @login_required
# @lecturer_required
# def delete_staff(request, pk):
#     staff = get_object_or_404(User, pk=pk)
#     staff.delete()
#     return redirect('lecturer_list')


@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, "Lecturer " + full_name + " has been deleted.")
    return redirect("lecturer_list")


# ########################################################


##########################################################
# organization views
##########################################################
@login_required
@admin_required
def organization_add_view(request):
    if request.method == "POST":
        form = OrganizationAddForm(
            request.POST, request.FILES
        )  # Include request.FILES for image fields
        if form.is_valid():
            organization = form.save()
            messages.success(
                request,
                f"Organization '{organization.name}' has been created successfully.",
            )
            return redirect("organization_list")  # Adjust the redirect URL as needed
        else:
            messages.error(request, "Correct the error(s) below.")
    else:
        form = OrganizationAddForm()
    return render(
        request,
        "accounts/add_organization.html",  # Adjust the path to your template
        {"title": "Add Organization", "form": form},
    )


@login_required
@admin_required
def edit_organization(request, pk):
    instance = get_object_or_404(Organization, pk=pk)
    print("=======instancesss-----", instance.__dict__)
    if request.method == "POST":
        form = OrganizationAddForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            organization = form.save()

            messages.success(
                request, f"Organization '{organization.name}' has been updated."
            )
            return redirect("organization_list")  # Adjust the redirect URL as needed
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = OrganizationAddForm(instance=instance)

    return render(
        request,
        "accounts/edit_organization.html",  # Adjust the template path
        {
            "title": "Edit Organization",
            "form": form,
        },
    )


@login_required
@admin_required
def delete_organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    organization_name = (
        organization.name
    )  # Capture the name before deletion for the success message
    organization.delete()
    messages.success(request, f"Organization '{organization_name}' has been deleted.")
    return redirect(
        "organization_list"
    )  # Adjust this to the name of your organization list view's URL name


# ########################################################
# Student views
# ########################################################
@login_required
@admin_required
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account for " + first_name + " " + last_name + " has been created.",
            )
            return redirect("student_list")
        else:
            messages.error(request, "Correct the error(s) below.")
    else:
        form = StudentAddForm()

    return render(
        request,
        "accounts/add_student.html",
        {"title": "Add Student", "form": form},
    )


@login_required
@admin_required
def edit_student(request, pk):
    # instance = User.objects.get(pk=pk)
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ("Student " + full_name + " has been updated."))
            return redirect("student_list")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(
        request,
        "accounts/edit_student.html",
        {
            "title": "Edit-profile",
            "form": form,
        },
    )


@method_decorator([login_required, admin_required], name="dispatch")
class StudentListView(FilterView):
    filterset_class = StudentFilter
    template_name = "accounts/student_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Students"
        return context


@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # full_name = student.user.get_full_name
    student.delete()
    messages.success(request, "Student has been deleted.")
    return redirect("student_list")


# ########################################################


class ParentAdd(CreateView):
    model = Parent
    form_class = ParentAddForm
    template_name = "accounts/parent_form.html"


# def parent_add(request):
#     if request.method == 'POST':
#         form = ParentAddForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('student_list')
#     else:
#         form = ParentAddForm(request.POST)
