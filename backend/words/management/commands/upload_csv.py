import csv
from django.core.management.base import BaseCommand
from words.database_functions import update_or_create_word, create_synonym
from django.utils import timezone
from datetime import datetime


class Command(BaseCommand):
    help = "Upload words from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument(
            "language",
            type=str,
            help="Language of the words (default: en)",
        )
        parser.add_argument(
            "translation",
            type=str,
            help="Language of the translations in the CSV file",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        lang = options["language"]
        translation_lang = options["translation"]

        self.stdout.write(self.style.SUCCESS(f"Processing file: {csv_file}"))

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                word = row["word"]
                translation = row["translation"]
                last_seen = row["last_seen"]
                strength = row["strength"]
                # Process each row as needed
                self.stdout.write(f"{word}, {translation}, {last_seen}, {strength}")

                # Update or create the word
                try:
                    dt = datetime.fromisoformat(last_seen)
                    if timezone.is_naive(dt):
                        last_seen = timezone.make_aware(dt)
                    else:
                        last_seen = dt

                    word_obj = update_or_create_word(
                        word=word,
                        language=lang,
                        strength=int(strength),
                        last_seen=last_seen,
                    )

                    # Split the translation field by commas, strip whitespace, and add each as a synonym
                    if translation:
                        translations = [
                            t.strip() for t in translation.split(",") if t.strip()
                        ]
                        for trans_word in translations:
                            try:
                                # Create or update the translation word
                                trans_obj = update_or_create_word(
                                    word=trans_word,
                                    language=translation_lang,
                                )
                                # Add synonym relationship between the main word and the translation
                                create_synonym(word_obj, trans_obj)
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"Error processing synonym '{trans_word}' for '{word}': {e}"
                                    )
                                )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing word '{word}': {e}")
                    )
