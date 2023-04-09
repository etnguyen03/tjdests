import argparse
import csv

from django.core.management.base import BaseCommand

from ...models import College


class Command(BaseCommand):
    help = "Imports a CSV containing college information."

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("file_name", type=str)

    def handle(self, *args, **options):
        """CSV format:

        College, City, State, Country
        """
        with open(options["file_name"], "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for line in reader:
                processed_location = ", ".join(
                    item
                    for item in [line["City"], line["State"], line["Country"]]
                    if item and item != "UNITED STATES"
                )  # country is assumed to be US
                result = College.objects.update_or_create(
                    name=line["College"],
                    location=processed_location,
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
