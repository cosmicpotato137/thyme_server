from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import traceback

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


def printrun_view(request):
    response = None
    if request.method == "POST":
        command = request.POST.get("command")
        if command:
            try:
                print("here")
                process = subprocess.Popen(
                    ["pronsole"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=command)
                response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
            except Exception as e:
                stack_trace = traceback.format_exc()
                response = f"<pre>Error: {str(e)}</pre><pre>{stack_trace}</pre>"
    return render(request, "pronsole.html", {"response": response})