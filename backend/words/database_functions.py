from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

    return word, created


def get_word(word, language=None):
    query = models.Word.objects.filter(word=word)
    if language:
        assert_valid_language(language)
        query = query.filter(language=language)

    if query.count() > 1:
        raise LookupError("Multiple words found, please specify a language.")
    elif query.count() == 0 and language == None:
        raise ValueError(f"Word '{word}' does not exist.")
    elif query.count() == 0:
        raise ValueError(f"Word '{word}' in language '{language}' does not exist.")
    else:
        return query.first()


def remove_word(word, language=None):
    """Remove a word from the database."""
    word = get_word(word, language)
    word.delete()


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
    p = 1.0
    p *= sigmoid(word.strength, 1000, 0.5)

    # Adjust probability based on the time since the word was last seen
    elapsed_time = timezone.now() - word.last_seen
    elapsed_time = elapsed_time.total_seconds()
    max_last_seen = models.Word.objects.filter(language=word.language).aggregate(
        Max("last_seen")
    )["last_seen__max"]
    if max_last_seen and hasattr(max_last_seen, "second") and max_last_seen.second != 0:
        elapsed_time /= max_last_seen.second
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
        raise ValueError("No words found.")

    # Return a word weighted by its p values
    p_values = query.values_list("p", flat=True)
    # Normalize
    s = np.sum(p_values)
    p_values = [p / s for p in p_values]
    return np.random.choice(list(query), p=p_values)


def get_words_list(language=None, page=1, per_page=10):
    query = models.Word.objects.all().order_by("language", "word")

    if language:
        query = query.filter(language=language)  # fixed typo

    paginator = Paginator(query, per_page)

    try:
        words_page = paginator.page(page)
    except PageNotAnInteger:
        page = 1
    except EmptyPage:
        page = paginator.num_pages
    finally:
        words_page = paginator.page(page)

    return (words_page, paginator.num_pages, page, query.count())


def update_word_synonyms(word_str, language, synonym_strs, synonym_language):
    """
    Update the synonyms of a word, adding new synonym words to the database if needed.
    This will replace the word's synonyms with the provided list.
    Args:
        word_str (str): The word whose synonyms to update.
        language (str): The language of the word and synonyms.
        synonym_strs (list[str]): List of synonym words (strings).
    Returns:
        word (models.Word): The updated word object.
        created_synonyms (list[models.Word]): List of synonym Word objects created.
    """
    # Get or create the main word
    word = get_word(word=word_str, language=language)

    # Prepare synonym Word objects
    created_synonyms = []
    for s in synonym_strs:
        try:
            synonym, _ = update_or_create_word(word=s, language=synonym_language)
            create_synonym(word=word, synonym=synonym)
            created_synonyms.append(synonym)
        except Exception as e:
            pass

    # Set the synonyms (replace existing)
    return word, created_synonyms
