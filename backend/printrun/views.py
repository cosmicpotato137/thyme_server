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
                process.stdin.write("connect\n")
                print("here")
                process.stdin.flush()
                process.wait(10)
                if "Printer is now online" in stdout:
                    print("here")
                    input = f"{command}\n"
                    process.stdin.write(input)
                    process.stdin.flush()
                print("here")
                stdout, stderr = process.communicate(input="exit", timeout=30)
                response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                response = f"<pre>Command timed out.</pre><pre>{stderr}</pre>"
            except Exception as e:
                traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                response = f"<pre>An error occurred: {str(e)}</pre><pre>{traceback_str}</pre>"
    return render(request, "pronsole.html", {"response": response})
