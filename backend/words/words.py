from terminal.terminal import Command, Parameter, Terminal, default_terminal
from words.models import Word
from words.database_functions import create_or_update_word, assert_valid_language


words_terminal = Terminal(prompt="words> ")


def add(word: str, language: str = "en", difficulty: int = 0):
    w = Word(
        word=word,
        language=language,
        difficulty=difficulty,
    )
    try:
        create_or_update_word(w)
    except Exception as e:
        return f"Error adding word: {e}"


def remove(word: str, language: str = None):
    """Remove a word from the database."""
    if language:
        try:
            word_obj = Word.objects.get(word=word, language=language)
            word_obj.delete()
        except Word.DoesNotExist:
            return f"Word '{word}' not found in the database."
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

    words = words.order_by("difficulty", "word")

    if not words.exists():
        return f"No words found for language '{language}'."

    return "\n".join(
        f"{word.word} ({word.language}, Difficulty: {word.difficulty})"
        for word in words
    )


words_commands = [
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
            Parameter(
                "difficulty",
                int,
                "The difficulty level of the word.",
                required=False,
                ailias="d",
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
