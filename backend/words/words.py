from terminal.terminal import Command, Parameter, Terminal, default_terminal
from words.models import Word
from words.database_functions import (
    update_or_create_word,
    assert_valid_language,
    remove_word,
)


words_terminal = Terminal(prompt="words> ")


def add(word: str, language: str = "en"):
    try:
        update_or_create_word(word, language)
    except Exception as e:
        return f"Error adding word: {e}"


def remove(word: str, language: str = None):
    """Remove a word from the database."""
    if language:
        try:
            remove_word(word, language)
        except Exception as e:
            return e
    else:
        word_objs = Word.objects.filter(word=word)
        if not word_objs.exists():
            return f"Word '{word}' not found in the database."
        if word_objs.count() > 1:
            return (
                f"Multiple entries found for word '{word}'. Please specify a language."
            )
        word_objs.first().delete()

    return f"Word '{word}' removed successfully."


def list(language: str = None):
    """List all words in the database for a given language."""
    if language:
        assert_valid_language(language)

    words = Word.objects.all()
    if language:
        words = words.filter(language=language)

    words = words.order_by("word", "language", "strength")

    if not words.exists():
        return f"No words found for language '{language}'."

    return "\n".join(
        f"{word.word} ({word.language}, {word.strength})" for word in words
    )


def list_synonyms(language: str, translation_language: str, max: int = 10):
    """List all synonyms for words in a specific language, showing their synonyms in another language."""
    assert_valid_language(language)
    assert_valid_language(translation_language)

    words = Word.objects.filter(language=language)
    results = []
    for word in words:
        synonyms = word.synonyms.filter(language=translation_language)
        for synonym in synonyms:
            results.append(f"{word.word} -> {synonym.word}")
            if len(results) >= max:
                break
        if len(results) >= max:
            break

    if not results:
        return f"No synonyms found for language '{language}' and translation language '{translation_language}'."

    return "\n".join(results)


def update(word: str, new_word: str, language: str = "en"):
    """Update a word in the database."""
    try:
        word_obj = Word.objects.get(word=word, language=language)
        word_obj.word = new_word
        word_obj.save()
        return f"Word '{word}' updated to '{new_word}' in language '{language}'."
    except Word.DoesNotExist:
        return f"Word '{word}' not found in language '{language}'."
    except Exception as e:
        return f"Error updating word: {e}"


words_commands = [
    Command(
        list_synonyms,
        description="List all synonyms for a given word in a specific language.",
    ),
    Command(
        add,
        description="Add or update a word in the database.",
        params=[
            Parameter("word", str, "The word to add or update.", positional=True),
            Parameter(
                "language",
                str,
                "The language of the word.",
                required=False,
                ailias="l",
            ),
        ],
    ),
    Command(
        remove,
        description="Remove a word from the database.",
        params=[
            Parameter("word", str, "The word to remove.", positional=True),
            Parameter(
                "language",
                str,
                "The language of the word to remove.",
                required=False,
                ailias="l",
            ),
        ],
    ),
    Command(
        list,
        description="List all words in the database for a given language.",
    ),
]

for command in words_commands:
    words_terminal.attach_command(command)
