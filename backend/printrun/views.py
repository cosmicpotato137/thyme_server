from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import traceback
import os
import getpass

from django.shortcuts import render


def printrun_view(request):
    response = None
    current_user = getpass.getuser()  # Get the current user
    print(f"Current user: {current_user}")  # Print the current user to the console or log

    if request.method == "POST":
        command = request.POST.get("command")
        if command:
            process = subprocess.Popen(
                ["pronsole"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=command)
            response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
    return render(request, "pronsole.html", {"response": response})