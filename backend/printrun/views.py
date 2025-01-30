from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import traceback
import os

from django.shortcuts import render


def pronsole_view(request):
    response = None
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