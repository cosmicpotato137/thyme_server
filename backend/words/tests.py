from django.test import TestCase
from django.utils import timezone
from words import models, database_functions


class DatabaseFunctionsTestCase(TestCase):
    def setUp(self):
        self.language = "en"
        self.word = models.Word.objects.create(
            word="TestWord",
            language=self.language,
            strength=3,
            difficulty=10,
            last_seen=timezone.now(),
            p=0.5,
        )

    def test_create_or_update_word_new(self):
        word = models.Word.objects.create(
            word="AnotherWord",
            language=self.language,
            difficulty=2,
            strength=2,
            last_seen=timezone.now(),
            p=0.1,
        )
        database_functions.create_or_update_word(word)
        self.assertTrue(models.Word.objects.filter(word="anotherword").exists())

    def test_create_or_update_word_existing(self):
        self.word.difficulty = 100
        max_difficulty = database_functions.get_max_difficulty(self.language)
        database_functions.create_or_update_word(self.word)
        self.assertEqual(self.word.difficulty, max_difficulty)

    def test_dec_strength(self):
        orig_strength = self.word.strength
        database_functions.dec_strength(self.word, 1)
        self.word.refresh_from_db()
        self.assertEqual(self.word.strength, orig_strength - 1)

    def test_inc_strength(self):
        self.word.strength = 1
        self.word.save()
        database_functions.inc_strength(self.word, 1)
        self.word.refresh_from_db()
        self.assertEqual(self.word.strength, 2)

    def test_get_max_difficulty(self):
        max_diff = database_functions.get_max_difficulty(self.language)
        self.assertTrue(isinstance(max_diff, int) or max_diff is None)
        self.assertEqual(max_diff, self.word.difficulty)

    def test_set_probability(self):
        self.word.last_seen = timezone.now() - timezone.timedelta(seconds=10)
        self.word.save()
        database_functions.set_probability(self.word)
        self.word.refresh_from_db()
        self.assertIsNotNone(self.word.p)

    def test_get_random_word(self):
        word = database_functions.get_weighted_word(language=self.language)
        self.assertIsInstance(word, models.Word)

    def test_get_random_word_empty(self):
        models.Word.objects.all().delete()
        word = database_functions.get_weighted_word(language=self.language)
        self.assertIsInstance(word, models.Word)
        self.assertEqual(word.word, "Oops")
