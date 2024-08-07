# Generated by Django 4.0.8 on 2024-06-06 10:44

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0016_alter_course_semester'),
        ('core', '0007_newsandevents_tags'),
        ('accounts', '0023_alter_student_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='TakenCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semesters', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('First', 'First'), ('Second', 'Second'), ('Third', 'Third')], max_length=10), blank=True, default=['First', 'Second', 'Third'], help_text='List of semesters', size=None)),
                ('assignment', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('mid_exam', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('quiz', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('attendance', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('final_exam', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('total', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('grade', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('A+', 'A+'), ('A', 'A'), ('A-', 'A-'), ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'), ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'), ('D', 'D'), ('F', 'F'), ('NG', 'NG')], max_length=2), blank=True, default=list, size=None)),
                ('point', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5), blank=True, default=list, size=None)),
                ('comment', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('PASS', 'PASS'), ('FAIL', 'FAIL')], max_length=200), blank=True, default=list, size=None)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taken_courses', to='course.course')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.session')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gpa', models.FloatField(null=True)),
                ('cgpa', models.FloatField(null=True)),
                ('semesters', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('First', 'First'), ('Second', 'Second'), ('Third', 'Third')], max_length=10), blank=True, default=['First', 'Second', 'Third'], help_text='List of semesters', size=None)),
                ('level', models.CharField(choices=[('Bachlor', 'Bachlor Degree'), ('Master', 'Master Degree'), ('College', 'College Degree'), ('Schooling', 'Schooling Degree')], max_length=25, null=True)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.session')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student')),
            ],
        ),
    ]
