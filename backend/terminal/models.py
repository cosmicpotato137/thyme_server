from django.db import models


class CommandHistory(models.Model):
    """
    Model to store the history of commands executed in the terminal.
    """

    command = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.command} at {self.timestamp}"

    @staticmethod
    def get_last_command(i: int):
        """
        Get the most recent command history entries.
        :param limit: Number of recent entries to retrieve.
        :return: QuerySet of CommandHistory objects.
        """
        query = CommandHistory.objects.order_by("-timestamp")
        if i >= len(query):
            i = len(query) - 1
        return ((query[i] if i >= 0 else None), i)
