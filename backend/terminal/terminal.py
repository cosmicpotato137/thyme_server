import inspect
import logging
import terminal.models as models
from terminal.input_handler import InputHandler
import re


class Parameter:
    """
    Represents a command parameter with description, required flag, and datatype.
    If datatype is None, the parameter is treated as a flag (boolean).
    """

    def __init__(
        self,
        name,
        datatype,
        description,
        required=False,
        ailias=None,
        positional=False,
    ):
        self.name = name
        self.description = description
        self.required = required
        self.datatype = datatype  # e.g., str, int, float, None for flag
        self.ailias = ailias  # Optional alias for the parameter
        self.positional = positional

    def __repr__(self):
        ailias_str = f"alias: -{self.ailias}, " if self.ailias else ""
        type_name = "type: " + (self.datatype.__name__ if self.datatype else "flag")
        required_str = ", required" if self.required and not self.positional else ""
        name_str = f"{self.name}" if self.positional else f"--{self.name}"
        return f"{name_str} ({ailias_str}{type_name}{required_str}): {self.description}"


class Command:
    """
    Represents a command with a callable, parameter hints, and a description.
    """

    def __init__(self, func, name=None, description="", params=None):
        """
        :param func: The function to execute.
        :param name: Optional command name (defaults to func.__name__).
        :param description: Description of the command.
        :param params: List of Parameter instances.
        """
        if not callable(func):
            raise ValueError("func must be callable")
        self.func = func
        self.name = name or func.__name__
        self.description = description
        # If params are provided, use them; otherwise, infer from function signature
        if params is not None:
            self.params = params
        else:
            self.params = []
            sig = inspect.signature(func)
            for name, param in sig.parameters.items():
                # Skip 'self' for instance methods
                if name == "self":
                    continue
                # Try to infer type from annotation, or None if not annotated
                if param.annotation != inspect.Parameter.empty:
                    datatype = param.annotation
                else:
                    raise ValueError(
                        "Parameter type must be specified or None for flags."
                    )
                positional = param.default == inspect.Parameter.empty
                name = param.name
                ailias = None
                if not filter(lambda x: x.ailias == name[0], self.params):
                    # Check if the first character can be used as an alias
                    ailias = name[0] if len(name) > 1 else None

                desc = ""
                # If there's a docstring, try to extract parameter descriptions (optional)
                if func.__doc__:
                    doc_lines = func.__doc__.splitlines()
                    for line in doc_lines:
                        if line.strip().startswith(name + ":"):
                            desc = line.strip()
                            break
                self.params.append(
                    Parameter(
                        name,
                        description=desc,
                        positional=positional,
                        datatype=datatype,
                        ailias=ailias,
                    )
                )

        # Check that there are no duplicate parameter names or aliases
        param_names = {p.name for p in self.params}
        param_aliases = {p.ailias for p in self.params if p.ailias}
        if len(param_names) != len(self.params):
            raise ValueError("Duplicate parameter names found in command parameters.")
        if len(param_aliases) != len([p for p in self.params if p.ailias]):
            raise ValueError("Duplicate parameter aliases found in command parameters.")

    def __call__(self, *args, **kwargs):
        if kwargs.get("h") or kwargs.get("help"):
            return self.help_statement()

        # Validate parameters
        position = 0
        new_kwargs = {}
        for param in self.params:
            if (
                param.required
                and not param.positional
                and param.name not in kwargs
                and param.ailias not in kwargs
            ):
                raise ValueError(f"Missing required parameter: {param.name}")
            if param.name in kwargs or param.ailias in kwargs:
                if param.ailias and param.ailias in kwargs:
                    value = kwargs[param.ailias]
                else:
                    value = kwargs[param.name]

                # Try to convert the value to the specified datatype
                try:
                    new_kwargs[param.name] = param.datatype(value)
                except ValueError:
                    raise ValueError(
                        f"Invalid value for parameter '{param.name}': "
                        f"expected {param.datatype.__name__}, got {value}"
                    )
            # Handle positional parameters
            if param.positional:
                if position < len(args):
                    value = args[position]
                    if param.datatype:
                        try:
                            value = param.datatype(value)
                        except ValueError:
                            raise ValueError(
                                f"Invalid value for positional parameter '{param.name}': "
                                f"expected {param.datatype.__name__}, got {value}"
                            )
                    new_kwargs[param.name] = value
                else:
                    raise ValueError(
                        f"Missing required positional parameter: {param.name}"
                    )
                position += 1

        return self.func(**new_kwargs)

    def help_statement(self):
        """
        Returns a formatted help statement for the command.
        """
        param_hints = "\n\t".join(str(param) for param in self.params)
        return (
            f"{self.name} - {self.description}\n\t{param_hints}"
            if param_hints
            else f"{self.name} - {self.description}"
        )

    def get_param_hints(self):
        """
        Returns parameter hints as a list.
        """
        return self.params

    def get_description(self):
        return self.description


class Terminal(InputHandler):
    def __init__(self, commands=[], prompt="> "):
        super().__init__(prompt)

        self._commands = {
            "help": Command(
                lambda: self.help_statement(),
                name="help",
                description="List all available commands.",
                params=[],
            )
        }
        for command in commands:
            self.attach_command(command)

    def _parse_command(self, command):
        command_split = command.split()
        command = command_split[0] if command_split else None
        args = []
        kwargs = {}
        for item in command_split[1:]:
            if item.startswith("--") and "=" in item:
                # Handle long options with '=' (e.g., --option=value)
                key, value = item[2:].split("=", 1)
                kwargs[key] = value
            elif item.startswith("--"):
                # Handle long options with space (e.g., --option value)
                key = item[2:]
                # Only add as kwarg if next item exists and is not a command
                next_index = command_split.index(item) + 1
                if next_index < len(command_split) and not command_split[
                    next_index
                ].startswith("-"):
                    kwargs[key] = command_split[next_index]
                else:
                    kwargs[key] = True
            elif item.startswith("-") and "=" in item:
                # Handle short options with '=' (e.g., -o=value)
                key, value = item[1:].split("=", 1)
                kwargs[key] = value
            elif item.startswith("-"):
                # Handle short options with space (e.g., -o value)
                key = item[1:]
                next_index = command_split.index(item) + 1
                if next_index < len(command_split) and not command_split[
                    next_index
                ].startswith("-"):
                    kwargs[key] = command_split[next_index]
                else:
                    kwargs[key] = True
            else:
                args.append(item)

        return command, args, kwargs

    def handle_input(self, input: str):
        """Default command handler if no specific command is found."""
        if input.strip() == "":
            return ("", True)

        models.CommandHistory.objects.create(command=input)

        command, args, kwargs = self._parse_command(input)

        if command not in self._commands:
            return ("Command not found.\n", True)

        try:
            matched_command = None
            for key in self._commands:
                # Match the entire command string to the regex pattern of the key
                if re.fullmatch(key, command):
                    matched_command = self._commands[key]
                    break
            if matched_command is None:
                return ("Command not found.\n", True)
            result = matched_command(*args, **kwargs)
            if result == "" or result is None:
                return ("", True)
            return (result + "\n"), True
        except Exception as e:
            return (f"Error executing command '{command}': {str(e)}" + "\n"), True

    def attach_command(self, command: Command):
        """Attach a Command instance to the terminal."""
        if not isinstance(command, Command):
            raise ValueError("All commands must be instances of Command class.")
        if command.name in self._commands:
            logging.info(f"Command '{command.name}' is already attached")
        self._commands[command.name] = command

    def detach_command(self, name):
        """Detach a command from the terminal."""
        if name in self._commands:
            del self._commands[name]

    def help_statement(self):
        """List all attached commands."""
        return "\n".join(cmd.help_statement() for cmd in self._commands.values())

    def create_relation(
        self,
        input_context_handler,
        child,
        command_name,
        command_description="",
        welcome_message="",
    ):
        """
        Create a relation between two terminals with a command.
        """

        def switch_terminals():
            """
            Switch to the child terminal.
            """
            input_context_handler.push_handler(child)
            return welcome_message

        def exit_terminal():
            """
            Exit the child terminal and return to the parent terminal.
            """
            if input_context_handler.pop_handler() is None:
                raise ValueError("No terminal to exit from")

        self.attach_command(
            Command(
                switch_terminals,
                name=command_name,
                description=command_description,
            )
        )
        child.attach_command(
            Command(
                exit_terminal,
                name="exit",
                description="Exit the current terminal",
            )
        )


default_terminal = Terminal(
    [
        Command(
            lambda: "",
            name="clear",
            description="Clears the terminal output.",
        ),
        Command(
            lambda: "Terminal access is available",
            name="status",
            description="Returns a message indicating terminal access is available.",
        ),
        Command(
            lambda: "",
            name="clear",
            description="Clears the terminal output.",
        ),
    ],
    prompt="user@terminal:~$ ",
)
