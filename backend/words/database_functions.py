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


def create_or_update_word(word: models.Word):
    word.word = word.word.lower()

    # Check if word has a valid language
    assert_valid_language(word.language)

    max_difficulty = get_max_difficulty(word.language, exclude=word)
    if word.difficulty > max_difficulty:
        word.difficulty = max_difficulty + 1
        word.save()
    else:
        models.Word.objects.filter(
            language=word.language, difficulty__gte=word.difficulty
        ).exclude(language=word.language, word=word.word).update(
            difficulty=F("difficulty") + 1
        )
        word.save()


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


def get_max_difficulty(language, exclude: models.Word = None):
    query = models.Word.objects.filter(language=language)
    if exclude and exclude.id:
        query.exclude(id=exclude.id)
    if not query.exists():
        return 0

    return query.aggregate(Max("difficulty"))["difficulty__max"]


def set_probability(word: models.Word):
    # Aggregate the difficulties of all words in the same language
    p = 2 - word.difficulty / get_max_difficulty(word.language)

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


def get_weighted_word(language=None, difficulty_range=None):
    query = models.Word.objects.all()
    if language:
        query = query.filter(language=language)
    if difficulty_range:
        # Normalize difficulty from 0-10
        max_difficulty = get_max_difficulty(language)
        normalized_range = (
            difficulty_range[0] * max_difficulty // 10,
            difficulty_range[1] * max_difficulty // 10,
        )
        query = query.filter(difficulty__range=normalized_range)
    if not query.exists():
        return models.Word(word="Oops")

    # Return a word weighted by its p values
    p_values = query.values_list("p", flat=True)
    # Normalize
    s = np.sum(p_values)
    p_values = [p / s for p in p_values]
    return np.random.choice(list(query), p=p_values)
