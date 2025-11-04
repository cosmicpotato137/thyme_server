from django.test import TestCase
from django.utils import timezone
from words.database_functions import (
    update_or_create_word,
    dec_strength,
    inc_strength,
    set_probability,
    get_weighted_word,
    update_word_synonyms,
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
        word_str = "AnotherWord"
        update_or_create_word(
            word_str, self.language, strength=2, last_seen=timezone.now()
        )
        self.assertTrue(
            models.Word.objects.filter(word=word_str, language=self.language).exists()
        )

    def test_create_or_update_word_existing(self):
        self.word.strength = 100
        self.word.save()
        updated_word, _ = update_or_create_word(
            self.word.word, self.word.language, strength=100
        )
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
        with self.assertRaises(ValueError):
            get_weighted_word(language=self.language)

    def test_update_word_synonyms(self):
        # Create a word and some synonyms
        main_word = "apple"
        synonyms = ["fruit", "macintosh", "pome"]
        synonym_language = self.language

        # Ensure only 'apple' exists at first
        update_or_create_word(main_word, self.language)
        for s in synonyms:
            self.assertFalse(
                models.Word.objects.filter(word=s, language=synonym_language).exists()
            )

        # Update synonyms
        word_obj, created_synonyms = update_word_synonyms(
            main_word, self.language, synonyms, synonym_language
        )

        # Check all synonyms now exist
        for s in synonyms:
            self.assertTrue(
                models.Word.objects.filter(word=s, language=synonym_language).exists()
            )

        # Check main word's synonyms are correct
        word_obj.refresh_from_db()
        self.assertEqual(
            set(word_obj.synonyms.values_list("word", flat=True)), set(synonyms)
        )

        # Check bidirectionality: each synonym has main_word as a synonym
        for s in synonyms:
            syn_obj = models.Word.objects.get(word=s, language=synonym_language)
            self.assertIn(main_word, syn_obj.synonyms.values_list("word", flat=True))
