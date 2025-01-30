from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import traceback
import os
import getpass

def printrun_view(request):
    response = None
    if request.method == "POST":
        command = request.POST.get("command")
        if command:
            try:
                # Start the pronsole process
                process = subprocess.Popen(
                    ["pronsole"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Send the connect command and wait for it to complete
                process.stdin.write("connect\n")
                process.stdin.flush()
                
                # Read the output until the printer is online
                while True:
                    line = process.stdout.readline()
                    if "Printer is now online" in line:
                        break
                    if not line:
                        raise Exception("Failed to connect to printer")
                
                # Send the actual command
                process.stdin.write(f"{command}\n")
                process.stdin.flush()
                
                # Read the output of the command
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