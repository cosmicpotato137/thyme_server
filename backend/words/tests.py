from django.test import TestCase
from django.utils import timezone
from words.database_functions import (
    update_or_create_word,
    dec_strength,
    inc_strength,
    set_probability,
    get_weighted_word,
)
import words.models as models


class DatabaseFunctionsTestCase(TestCase):
    def setUp(self):
        self.language = "en"
        self.word = models.Word.objects.create(
            word="TestWord",
            language=self.language,
            strength=3,
            last_seen=timezone.now(),
            p=0.5,
        )

    def test_create_or_update_word_new(self):
        word = models.Word.objects.create(
            word="AnotherWord",
            language=self.language,
            strength=2,
            last_seen=timezone.now(),
            p=0.1,
        )
        update_or_create_word(word)
        self.assertTrue(models.Word.objects.filter(word="anotherword").exists())

    def test_create_or_update_word_existing(self):
        self.word.strength = 100
        updated_word = update_or_create_word(self.word)
        self.assertEqual(100, updated_word.strength)

    def test_dec_strength(self):
        orig_strength = self.word.strength
        dec_strength(self.word, 1)
        self.word.refresh_from_db()
        self.assertEqual(self.word.strength, orig_strength - 1)

    def test_inc_strength(self):
        self.word.strength = 1
        self.word.save()
        inc_strength(self.word, 1)
        self.word.refresh_from_db()
        self.assertEqual(self.word.strength, 2)

    def test_set_probability(self):
        self.word.last_seen = timezone.now() - timezone.timedelta(seconds=10)
        self.word.save()
        set_probability(self.word)
        self.word.refresh_from_db()
        self.assertIsNotNone(self.word.p)

    def test_get_random_word(self):
        word = get_weighted_word(language=self.language)
        self.assertIsInstance(word, models.Word)

    def test_get_random_word_empty(self):
        models.Word.objects.all().delete()
        word = get_weighted_word(language=self.language)
        self.assertIsInstance(word, models.Word)
        self.assertEqual(word.word, "Oops")
