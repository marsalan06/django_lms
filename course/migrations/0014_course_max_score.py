# Generated by Django 4.0.8 on 2024-05-02 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0013_course_credit_course_level_course_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='max_score',
            field=models.FloatField(default=100.0, null=True),
        ),
    ]