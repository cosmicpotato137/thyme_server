import words.models as models
from django.db.models import Max, F
from django.utils import timezone
import numpy as np


def assert_valid_language(language: str):
    """Assert that the given language is valid."""
    if language not in models.Languages.values:
        raise ValueError(
            f"Invalid language '{language}'. Must be one of {models.Languages.values}."
        )


def update_or_create_word(word, language, strength=0, last_seen=None):
    """Update or create a word in the database."""
    assert_valid_language(language)
    defaults = {
        "strength": strength,
    }
    if last_seen:
        defaults["last_seen"] = last_seen

    word, created = models.Word.objects.update_or_create(
        word=word,
        language=language,
        defaults=defaults,
    )

    return word


def remove_word(word, language):
    """Remove a word from the database."""
    assert_valid_language(language)
    try:
        word_instance = models.Word.objects.get(word=word, language=language)
        word_instance.delete()
    except models.Word.DoesNotExist:
        raise ValueError(f"Word '{word}' in language '{language}' does not exist.")


def create_synonym(word: models.Word, synonym: models.Word):
    """Create a synonym relationship between two words."""
    if word == synonym:
        raise ValueError("A word cannot be a synonym of itself.")

    # Ensure both words are saved in the database
    try:
        word.save()
        synonym.save()
    except Exception as e:
        pass

    word.synonyms.add(synonym)


def sigmoid(x, a, b):
    return 1 / (1 + pow(a, x - b))


def dec_strength(word: models.Word, ammount=1):
    if word.strength > 0:
        word.strength -= ammount
        word.save()


def inc_strength(word: models.Word, ammount=1):
    if word.strength < 5:
        word.strength += ammount
        word.save()


def set_probability(word: models.Word):
    # Show weaker words first
    p *= sigmoid(word.strength, 1000, 0.5)

    # Adjust probability based on the time since the word was last seen
    elapsed_time = timezone.now() - word.last_seen
    elapsed_time = elapsed_time.total_seconds()
    elapsed_time /= (
        models.Word.objects.filter(language=word.language)
        .aggregate(Max("last_seen"))["last_seen__max"]
        .second
    )
    p *= elapsed_time

    word.p = p
    word.save()


def get_weighted_word(language=None, pk_range=None):
    query = models.Word.objects.all()
    if language:
        query = query.filter(language=language)
    if pk_range:
        query = query.filter(pk__range=pk_range)
    if not query.exists():
        return models.Word(word="Oops")

    # Return a word weighted by its p values
    p_values = query.values_list("p", flat=True)
    # Normalize
    s = np.sum(p_values)
    p_values = [p / s for p in p_values]
    return np.random.choice(list(query), p=p_values)
