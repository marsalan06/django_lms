# Generated by Django 4.0.8 on 2024-08-08 06:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_session_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='semesters', to='core.session'),
        ),
    ]