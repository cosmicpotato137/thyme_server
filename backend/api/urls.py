from django.urls import path, include
from api import views

urlpatterns = [
    # Add your API endpoints here, for example:
    path("status/", views.get_status, name="get_status"),
    path("terminal/", views.terminal, name="terminal"),
    path("last-command/", views.get_last_command, name="get_last_command"),
    path("command-history/", views.post_command_history, name="post_command_history"),
    path("current-prompt/", views.current_prompt, name="current_prompt"),
]
