# Generated by Django 4.0.8 on 2024-04-29 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_merge_0019_user_gender_0020_alter_user_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='level',
            field=models.CharField(choices=[('Bachlor', 'Bachloar Degree'), ('Master', 'Master Degree')], max_length=25, null=True),
        ),
    ]
