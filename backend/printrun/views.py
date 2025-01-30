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
            try:
                process = subprocess.Popen(
                    ["pronsole"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input="connect", timeout=5)
                print(f"stdout: {stdout}")
                stdout, stderr = process.communicate(input=command, timeout=5)
                response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
                stdout, stderr = process.communicate(input="exit", timeout=5)
                print(f"stdout: {stdout}")
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                response = f"<pre>Command timed out.</pre><pre>{stderr}</pre>"
            except Exception as e:
                traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                response = f"<pre>An error occurred: {str(e)}</pre><pre>{traceback_str}</pre>"
    return render(request, "pronsole.html", {"response": response})