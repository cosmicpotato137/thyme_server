from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import traceback
import os

from django.shortcuts import render


def printrun_view(request):
    response = None
    if request.method == "POST":
        command = request.POST.get("command")
        if command:
            try:
                env = os.environ.copy()
                env['PRONSOLE_CONFIG_DIR'] = '/path/to/accessible/directory'
                process = subprocess.Popen(
                    ["pronsole"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                stdout, stderr = process.communicate(input=command)
                response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
            except Exception as e:
                stack_trace = traceback.format_exc()
                response = f"<pre>Error: {str(e)}</pre><pre>{stack_trace}</pre>"
    return render(request, "pronsole.html", {"response": response})