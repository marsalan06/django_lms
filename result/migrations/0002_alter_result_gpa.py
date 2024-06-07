import django.contrib.postgres.fields
from django.db import migrations, models


def drop_old_gpa_field(apps, schema_editor):
    # Get the Result model
    Result = apps.get_model("result", "Result")
    # Drop the old gpa field
    schema_editor.execute("ALTER TABLE result_result DROP COLUMN IF EXISTS gpa;")


class Migration(migrations.Migration):

    dependencies = [
        ("result", "0001_initial"),
    ]

    operations = [
        # First, remove the old gpa field
        migrations.RunPython(drop_old_gpa_field),
        # Now add the new gpa array field
        migrations.AddField(
            model_name="result",
            name="gpa",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.FloatField(null=True),
                blank=True,
                default=list,
                help_text="List of GPAs for each semester",
                size=3,
            ),
        ),
    ]
