# Generated by Django 3.2 on 2021-04-19 18:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("destinations", "0005_alter_decision_admission_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="college",
            name="ceeb_code",
            field=models.CharField(max_length=10, verbose_name="CEEB Code"),
        ),
    ]
