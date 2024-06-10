from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


from accounts.models import Student
from core.models import Semester, Session
from course.models import Course

YEARS = (
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (4, "5"),
    (4, "6"),
)

# LEVEL_COURSE = "Level course"
BACHLOR_DEGREE = "Bachlor"
MASTER_DEGREE = "Master"
COLLEGE_DEGREE = "College"
SCHOOL_DEGREE = "Schooling"

LEVEL = (
    # (LEVEL_COURSE, "Level course"),
    (BACHLOR_DEGREE, "Bachlor Degree"),
    (MASTER_DEGREE, "Master Degree"),
    (COLLEGE_DEGREE, "College Degree"),
    (SCHOOL_DEGREE, "Schooling Degree"),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

SEMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)

A_PLUS = "A+"
A = "A"
A_MINUS = "A-"
B_PLUS = "B+"
B = "B"
B_MINUS = "B-"
C_PLUS = "C+"
C = "C"
C_MINUS = "C-"
D = "D"
F = "F"
NG = "NG"

GRADE = (
    (A_PLUS, "A+"),
    (A, "A"),
    (A_MINUS, "A-"),
    (B_PLUS, "B+"),
    (B, "B"),
    (B_MINUS, "B-"),
    (C_PLUS, "C+"),
    (C, "C"),
    (C_MINUS, "C-"),
    (D, "D"),
    (F, "F"),
    (NG, "NG"),
)

PASS = "PASS"
FAIL = "FAIL"

COMMENT = (
    (PASS, "PASS"),
    (FAIL, "FAIL"),
)


class TakenCourseManager(models.Manager):
    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated():
                user_obj = user
        return self.model.objects.create(user=user_obj)


class TakenCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="taken_courses"
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, blank=True, null=True
    )
    semesters = ArrayField(
        models.CharField(max_length=10, choices=SEMESTER),
        blank=True,
        default=["First", "Second", "Third"],
        help_text="List of semesters",
    )
    assignment = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    mid_exam = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    quiz = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    attendance = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    final_exam = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    total = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    grade = ArrayField(
        models.CharField(choices=GRADE, max_length=2, blank=True),
        default=list,
        blank=True,
    )
    point = ArrayField(
        models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
        default=list,
        blank=True,
    )
    comment = ArrayField(
        models.CharField(choices=COMMENT, max_length=200, blank=True),
        default=list,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.course.slug})

    def __str__(self):
        return "{0} ({1})".format(self.course.title, self.course.code)

    def get_total(self, semester_index):
        try:
            current_total_score = (
                float(self.assignment[semester_index])
                + float(self.mid_exam[semester_index])
                + float(self.quiz[semester_index])
                + float(self.attendance[semester_index])
                + float(self.final_exam[semester_index])
            )
            if current_total_score > self.course.max_score:
                return float(self.course.max_score)
            else:
                return current_total_score
        except IndexError:
            return 0.0

    def get_grade(self, total):
        if total >= 90:
            grade = A_PLUS
        elif total >= 85:
            grade = A
        elif total >= 80:
            grade = A_MINUS
        elif total >= 75:
            grade = B_PLUS
        elif total >= 70:
            grade = B
        elif total >= 65:
            grade = B_MINUS
        elif total >= 60:
            grade = C_PLUS
        elif total >= 55:
            grade = C
        elif total >= 50:
            grade = C_MINUS
        elif total >= 45:
            grade = D
        elif total < 45:
            grade = F
        else:
            grade = NG
        return grade

    def get_comment(self, grade):
        if grade == F or grade == NG:
            comment = FAIL
        else:
            comment = PASS
        return comment

    def get_point(self, grade):
        credit = self.course.credit
        if grade == A_PLUS:
            point = 4
        elif grade == A:
            point = 4
        elif grade == A_MINUS:
            point = 3.75
        elif grade == B_PLUS:
            point = 3.5
        elif grade == B:
            point = 3
        elif grade == B_MINUS:
            point = 2.75
        elif grade == C_PLUS:
            point = 2.5
        elif grade == C:
            point = 2
        elif grade == C_MINUS:
            point = 1.75
        elif grade == D:
            point = 1
        else:
            point = 0
        return int(credit) * point

    def calculate_gpa(self, total_credit_in_semester, semester_index):
        current_semester = Semester.objects.get(is_current_semester=True)
        print("-----current0000sem----", current_semester)
        student_courses = TakenCourse.objects.filter(
            student=self.student,
            course__level=self.student.level,
            session=self.session,
            semesters__contains=[current_semester.semester],
        )
        print("-----courses-----", student_courses)
        total_points = 0
        for course in student_courses:
            print("------cours-----", course)
            total = course.get_total(semester_index)
            print("--------total-----", total)
            grade = course.get_grade(total)
            print("------grade----", grade)
            points = course.get_point(grade)
            print("------points-----", points)
            total_points += points
            print("------total points---", total_points)
        try:
            print("------total credit in sem----", total_credit_in_semester)
            gpa = total_points / total_credit_in_semester
            print("-----gpa----", gpa)
            return round(gpa, 2)
        except ZeroDivisionError:
            return 0

    def calculate_cgpa(self):
        print("----cgpa code-------")
        previous_results = Result.objects.filter(
            student=self.student, level__lte=self.student.level
        )
        total_gpa = 0
        count = 0

        for result in previous_results:
            for gpa in result.gpa:
                if gpa is not None:
                    total_gpa += gpa
                    count += 1

        try:
            cgpa = round(total_gpa / count, 2)
            return cgpa
        except ZeroDivisionError:
            return 0


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gpa = ArrayField(
        models.FloatField(null=True),
        size=3,  # Assuming three semesters
        default=list,
        blank=True,
        help_text="List of GPAs for each semester",
    )
    cgpa = models.FloatField(null=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, blank=True, null=True
    )
    semesters = ArrayField(
        models.CharField(max_length=10, choices=SEMESTER),
        blank=True,
        default=["First", "Second", "Third"],
        help_text="List of semesters",
    )
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
