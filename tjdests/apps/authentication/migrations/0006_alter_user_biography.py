# Generated by Django 3.2 on 2021-04-22 02:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0005_user_gpa"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="biography",
            field=models.TextField(blank=True, max_length=1000),
        ),
    ]
