# Generated by Django 4.0.8 on 2024-07-29 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0009_remove_descriptivequestion_explanation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='category',
            field=models.TextField(choices=[('assignment', 'Assignment'), ('exam', 'Exam'), ('practice', 'Practice Quiz')]),
        ),
    ]
