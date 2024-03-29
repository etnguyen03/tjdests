# Generated by Django 3.2 on 2021-04-21 01:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("destinations", "0006_alter_college_ceeb_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="decision",
            name="admission_status",
            field=models.CharField(
                choices=[
                    ("ADMIT", "Admitted"),
                    ("WAITLIST", "Waitlisted"),
                    ("WAITLIST_ADMIT", "Waitlist-Admitted"),
                    ("WAITLIST_DENY", "Waitlist-Denied"),
                    ("DEFER", "Deferred"),
                    ("DEFER_ADMIT", "Deferred-Admitted"),
                    ("DEFER_DENY", "Deferred-Denied"),
                    ("DEFER_WL_A", "Deferred-Waitlisted-Admitted"),
                    ("DEFER_WL_D", "Deferred-Waitlisted-Denied"),
                    ("DENY", "Denied"),
                ],
                max_length=20,
            ),
        ),
    ]
