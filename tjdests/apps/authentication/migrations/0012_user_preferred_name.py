# Generated by Django 3.2.12 on 2022-02-09 22:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0011_user_use_nickname"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="preferred_name",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
