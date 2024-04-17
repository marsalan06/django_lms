# Generated by Django 4.0.8 on 2024-04-06 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_alter_quiz_type_of_quiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='descriptivequestion',
            name='explanation',
        ),
        migrations.RemoveField(
            model_name='descriptivequestion',
            name='file',
        ),
        migrations.RemoveField(
            model_name='descriptivequestion',
            name='id',
        ),
        migrations.RemoveField(
            model_name='descriptivequestion',
            name='instructor_answer',
        ),
        migrations.RemoveField(
            model_name='descriptivequestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='descriptivequestion',
            name='quiz',
        ),
        migrations.AddField(
            model_name='descriptivequestion',
            name='keywords',
            field=models.TextField(blank=True, help_text='Comma-separated keywords that are expected in a correct answer.', verbose_name='Keywords'),
        ),
        migrations.AddField(
            model_name='descriptivequestion',
            name='question_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='quiz.question'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='descriptivequestion',
            name='sample_answer',
            field=models.TextField(blank=True, help_text='A model answer to guide evaluation or provide automated feedback.', verbose_name='Sample Answer'),
        ),
    ]