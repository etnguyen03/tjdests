import argparse
import csv

from django.core.management.base import BaseCommand

from ...models import College


class Command(BaseCommand):
    help = "Imports a CSV of CEEB codes as colleges"

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("file_name", type=str)

    def handle(self, *args, **options):
        """CSV format:

        CEEB, College Name, City, State
        """
        with open(options["file_name"], "r") as file:
            reader = csv.DictReader(file)

            for line in reader:
                # International colleges are treated specially because
                # they do not have CEEB codes.
                if line["CEEB"] == "INTL":
                    result = College.objects.update_or_create(
                        ceeb_code=line["CEEB"],
                        name=line["College Name"],
                        defaults={
                            "location": f"{line['City']}, {line['State']}",
                        },
                    )
                else:
                    result = College.objects.update_or_create(
                        ceeb_code=line["CEEB"],
                        defaults={
                            "name": line["College Name"],
                            "location": f"{line['City']}, {line['State']}",
                        },
                    )

                if result[1]:
                    self.stdout.write(
                        f"Added university {result[0].name}.",
                        style_func=self.style.SUCCESS,
                    )
                else:
                    self.stdout.write(
                        f"Did not update university {result[0].name}.",
                        style_func=self.style.WARNING,
                    )
