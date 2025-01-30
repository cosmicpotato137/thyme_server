from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import traceback
import os
import getpass

from django.shortcuts import render


def printrun_view(request):
    response = None
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
                input = "connect\n"
                stdout, stderr = process.communicate(input=input, timeout=30)
                process.wait(2)
                if "Printer is now online" in stdout:
                    input = f"{command}\n"
                    process.stdin.write(input)
                    process.stdin.flush()
                    stdout, stderr = process.communicate(timeout=30)
                response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                response = f"<pre>Command timed out.</pre><pre>{stderr}</pre>"
            except Exception as e:
                traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                response = f"<pre>An error occurred: {str(e)}</pre><pre>{traceback_str}</pre>"
    return render(request, "pronsole.html", {"response": response})
