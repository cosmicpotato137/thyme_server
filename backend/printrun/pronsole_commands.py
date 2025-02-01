import subprocess
import os
import select
import time


class PronsoleCommands:
    def __init__(self):
        self.process = subprocess.Popen(
            ["pronsole"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def send_command(self, command, args=None, timeout=5):
        if args:
            command = f"{command} {' '.join(args)}"
        self.process.stdin.write(f"{command}\n")
        self.process.stdin.flush()
        output = []

        return output

    def connect(self, port, baudrate):
        output = self.send_command("connect", [port, baudrate])
        for line in self.process.stdout:
            if "Printer is now online" in line:
                return output
        raise Exception("Failed to connect to printer")

    def exit(self):
        self.process.stdin.write("exit\n")
        self.process.stdin.flush()
        return self.process.communicate()

    def home(self, axis):
        return self.send_command("home", [axis])

    def move(self, axis, distance):
        return self.send_command("move", [axis, distance])

    def resume(self):
        return self.send_command("resume")

    def ls(self):
        return self.send_command("ls")

    def load(self, file):
        filepath = os.path.join("/tmp", file.name)
        with open(filepath, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        output = self.send_command("load", [filepath])
        os.remove(filepath)
        return output
