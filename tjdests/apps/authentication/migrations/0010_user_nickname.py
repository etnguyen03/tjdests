# Generated by Django 3.2.5 on 2021-07-28 02:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0009_user_last_modified"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="nickname",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
