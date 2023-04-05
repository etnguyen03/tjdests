# Generated by Django 3.2.12 on 2022-02-17 15:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0012_user_preferred_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="GPA",
            field=models.DecimalField(
                blank=True,
                decimal_places=3,
                help_text="Weighted GPA",
                max_digits=4,
                null=True,
            ),
        ),
    ]
