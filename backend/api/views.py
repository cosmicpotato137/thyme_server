from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from terminal.input_context_handler import input_context_handler
from words.words import words_terminal
from terminal.terminal import default_terminal
from terminal.models import CommandHistory
from django.utils.timezone import now


@api_view(["GET"])
def get_status(request):
    """
    API endpoint to check the status of the server.
    Returns a simple JSON response indicating the server is running.
    """
    return Response({"status": "Server is running"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_last_command(request):
    if not request.query_params.get("i"):
        return Response(
            {"error": "Parameter 'i' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    command, i = CommandHistory.get_last_command(int(request.query_params.get("i")))
    if not command:
        return Response(
            {"error": "No command history found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(
        {
            "command": command.command,
            "i": i,
            "message": f"Last command: {command.command}",
            "request": request.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def current_prompt(request):
    """
    API endpoint to get the current prompt of the terminal.
    Returns the current prompt string.
    """

    return Response(
        {
            "prompt": input_context_handler.get_handlers()[-1].prompt,
            "message": "Current prompt retrieved successfully.",
            "request": request.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def post_command_history(request):
    if not request.data.get("command"):
        return Response(
            {"error": "Parameter 'command' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    CommandHistory.objects.create(command=request.data.get("command"), timestamp=now())

    return Response(
        {
            "message": "Command history updated successfully.",
            "request": request.data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def terminal(request):
    """
    API endpoint to return a simple message for terminal access.
    This can be used to check if the API is accessible from a terminal.
    """
    default_terminal.create_relation(
        input_context_handler,
        words_terminal,
        "words",
        "Words study service.",
        "Welcome to the words terminal. Type 'help' for assistance.",
    )

    message, completed = input_context_handler.handle_input(
        request.data.get("command", "")
    )

    return Response(
        {
            "message": message,
            "level": "info" if completed else "error",
            "request": request.data,
        },
        status=status.HTTP_200_OK,
    )
