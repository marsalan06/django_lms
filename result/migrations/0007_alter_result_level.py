# Generated by Django 4.0.8 on 2024-04-29 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0006_alter_result_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='level',
            field=models.CharField(choices=[('Bachlor', 'Bachlor Degree'), ('Master', 'Master Degree'), ('College', 'College Degree'), ('Schooling', 'Schooling Degree')], max_length=25, null=True),
        ),
    ]
