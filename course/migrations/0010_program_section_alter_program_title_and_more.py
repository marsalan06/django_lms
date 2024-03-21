# Generated by Django 4.0.8 on 2024-02-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_alter_course_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='section',
            field=models.CharField(default='A', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='program',
            name='title',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterUniqueTogether(
            name='program',
            unique_together={('title', 'section')},
        ),
    ]