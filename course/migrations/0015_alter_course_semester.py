# Generated by Django 4.0.8 on 2024-05-31 15:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0014_course_max_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='semester',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('First', 'First'), ('Second', 'Second'), ('Third', 'Third')], max_length=10), blank=True, help_text='List of semesters', size=None),
        ),
    ]