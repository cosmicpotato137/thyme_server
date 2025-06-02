from django.db import models


class Languages(models.TextChoices):
    ENGLISH = "en", "English"
    SPANISH = "es", "Spanish"
    FRENCH = "fr", "French"
    GERMAN = "de", "German"
    ITALIAN = "it", "Italian"
    PORTUGUESE = "pt", "Portuguese"
    RUSSIAN = "ru", "Russian"
    CHINESE = "zh", "Chinese"
    JAPANESE = "ja", "Japanese"
    KOREAN = "ko", "Korean"


class Word(models.Model):
    word = models.CharField(max_length=255)
    language = models.CharField(
        max_length=2,
        choices=Languages.choices,
        default=Languages.ENGLISH,
    )
    difficulty = models.IntegerField(default=0)
    strength = models.IntegerField(default=0)

    p = models.FloatField(default=0.0)
    last_seen = models.DateTimeField(auto_now=True)

    synonyms = models.ManyToManyField(
        "Word",
        symmetrical=True,
        blank=True,
        through="Synonym",
    )

    def __str__(self):
        return self.word

    def get_synonyms(self, language=None):
        if language:
            return self.synonyms.filter(language=language)
        return self.synonyms.all()

    class Meta:
        ordering = ["word"]
        unique_together = [("word", "language"), ("difficulty", "language")]


class Synonym(models.Model):
    word = models.ForeignKey(Word, models.CASCADE, related_name="synonym_words")
    synonym = models.ForeignKey(Word, models.CASCADE, related_name="synonyms_related")

    class Meta:
        unique_together = ("word", "synonym")
