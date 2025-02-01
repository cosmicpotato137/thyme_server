from django.shortcuts import render
from django.http import HttpResponse
import traceback
import os
from printrun.pronsole_commands import PronsoleCommands


def printrun_view(request):
    response = None
    if request.method == "POST":
        command = request.POST.get("command")
        file = request.FILES.get("file")  # Get the uploaded file
        if command:
            pronsole = PronsoleCommands()
            try:
                pronsole.connect(
                    "/dev/ttyUSB0", "115200"
                )  # Adjust the port and baudrate as needed

                if command == "upload":
                    if not file:
                        response = "<pre>No file uploaded.</pre>"
                    else:
                        output = pronsole.load(file)
                else:
                    output = pronsole.send_command(command)

                stdout, stderr = pronsole.exit()
                response = f"<pre>{stdout}</pre><pre>{stderr}</pre>"
            except TimeoutError:
                stdout, stderr = pronsole.exit()
                response = f"<pre>Timeout error occurred.</pre><pre>{stdout}</pre><pre>{stderr}</pre>"
            except Exception as e:
                traceback_str = "".join(traceback.format_tb(e.__traceback__))
                response = (
                    f"<pre>An error occurred: {str(e)}</pre><pre>{traceback_str}</pre>"
                )
    return render(request, "pronsole.html", {"response": response})
