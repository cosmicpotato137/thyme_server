import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now

from terminal.input_context_handler import input_context_handler
from words.words import words_terminal
from terminal.terminal import default_terminal
from terminal.models import CommandHistory
from words import database_functions as wdbf
from words import serializers as wser


@api_view(["GET"])
def get_status(request):
    """Check if the server is running."""
    return Response({"status": "Server is running."}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_last_command(request):
    """Fetch the last command from command history for a given index `i`."""
    i = request.query_params.get("i")
    if not i:
        return Response(
            {"error": "Parameter 'i' is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        command, idx = CommandHistory.get_last_command(int(i))
    except (ValueError, TypeError):
        return Response(
            {"error": "Parameter 'i' must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not command:
        return Response(
            {"error": "No command history found."}, status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            "command": command.command,
            "i": idx,
            "message": f"Last command: {command.command}",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def post_command_history(request):
    """Store a new command in the history."""
    command = request.data.get("command")
    if not command:
        return Response(
            {"error": "Parameter 'command' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    CommandHistory.objects.create(command=command, timestamp=now())
    return Response(
        {"message": "Command history updated successfully."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def post_word(request):
    """Create or update a word in the database."""
    word = request.data.get("word")
    language = request.data.get("language")

    if not word or not language:
        return Response(
            {"error": "Missing required parameters: 'word' or 'language'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        word_obj, created = wdbf.update_or_create_word(word, language)
        message = (
            f"Created word {word_obj}."
            if created
            else f"Word {word_obj} already exists."
        )
        return Response(
            {"message": message},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_word(request):
    """Delete a word from the database."""
    word = request.data.get("word")
    language = request.data.get("language")

    if not word:
        return Response(
            {"error": "Missing required parameter: 'word'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        wdbf.remove_word(word, language)
        return Response(
            {"message": f"Word {word} deleted successfully."}, status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_304_NOT_MODIFIED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_word(request):
    """Retrieve a specific word and its metadata."""
    word = request.query_params.get("word")
    language = request.query_params.get("language")

    if not word:
        return Response(
            {"error": "Missing required parameter: 'word'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        word_obj = wdbf.get_word(word, language)
        return Response(
            {
                "message": f"Word '{word}' found.",
                "data": wser.WordSerializer(word_obj).data,
            },
            status=status.HTTP_200_OK,
        )
    except LookupError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_random_word(request):
    """Retrieve a random word, weighted by frequency or relevance."""
    language = request.query_params.get("language")
    if not language:
        return Response(
            {"error": "Missing required parameter: 'language'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        word_obj = wdbf.get_weighted_word(language)
        return Response(
            {
                "message": f"Word {word_obj.word} found.",
                "data": wser.WordSerializer(word_obj).data,
            },
            status=status.HTTP_200_OK,
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_words_list(request):
    """Paginated list of words, optionally filtered by language."""
    language = request.query_params.get("language")
    page = request.query_params.get("page", 1)
    per_page = request.query_params.get("per_page", 10)

    try:
        words, pages, page, total = wdbf.get_words_list(language, page, per_page)
        return Response(
            {
                "message": "Found page of words.",
                "data": wser.WordSerializer(words, many=True).data,
                "page": page,
                "pages": pages,
                "total": total,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def update_word_synonyms(request):
    """Update the synonyms of a word, adding new synonym words to the database if needed.
    This will replace the word's synonyms with the provided list."""
    word = request.data.get("word")
    language = request.data.get("language")
    synonym_list = request.data.get("synonym_list")
    synonym_language = request.data.get("synonym_language")

    if not word or not language or not synonym_list or not synonym_language:
        return Response(
            {
                "error": "Missing required parameters: 'word', 'language', 'synonym_list', or 'synonym_language'."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Parse synonym_list as a list
    if isinstance(synonym_list, str):
        # Try to parse as JSON array
        try:
            parsed = json.loads(synonym_list)
            if isinstance(parsed, list):
                synonym_list = parsed
            else:
                # Fallback: split by comma
                synonym_list = [s.strip() for s in synonym_list.split(",") if s.strip()]
        except Exception:
            # Fallback: split by comma
            synonym_list = [s.strip() for s in synonym_list.split(",") if s.strip()]
    elif not isinstance(synonym_list, list):
        # If not a list or string, make it a single-item list
        synonym_list = [str(synonym_list)]

    try:
        word_obj, synonyms = wdbf.update_word_synonyms(
            word_str=word,
            language=language,
            synonym_strs=synonym_list,
            synonym_language=synonym_language,
        )
        message = (
            f"Created synonyms {[s.word for s in synonyms]}."
            if synonyms and len(synonyms) > 0
            else f"No synonyms added."
        )
        return Response(
            {"message": message},
            status=(
                status.HTTP_201_CREATED
                if synonyms and len(synonyms) > 0
                else status.HTTP_200_OK
            ),
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
