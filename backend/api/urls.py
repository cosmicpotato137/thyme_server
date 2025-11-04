from django.urls import path, include
from api import views

urlpatterns = [
    # Add your API endpoints here, for example:
    path("status/", views.get_status, name="get_status"),
    path("last-command/", views.get_last_command, name="get_last_command"),
    path("command-history/", views.post_command_history, name="post_command_history"),
    path("word/", views.get_word, name="word"),
    path("post-word/", views.post_word, name="post_word"),
    path("random-word/", views.get_random_word, name="random_word"),
    path("delete-word/", views.delete_word, name="delete_word"),
    path("list-words/", views.get_words_list, name="list_words"),
    path(
        "update-word-synonyms/", views.update_word_synonyms, name="update_word_synonyms"
    ),
]
