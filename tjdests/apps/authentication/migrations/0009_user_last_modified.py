# Generated by Django 3.2 on 2021-04-23 17:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0008_alter_user_biography"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_modified",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
