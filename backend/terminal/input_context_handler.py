from terminal.terminal import default_terminal, Command
from words.words import words_terminal
from terminal.terminal import default_terminal


class InputContextHandler:
    _instance = None

    def __new__(cls, input_handlers=[]):
        if cls._instance is None:
            cls._instance = super(InputContextHandler, cls).__new__(cls)
            cls._instance.input_handlers = input_handlers
        return cls._instance

    def push_handler(self, handler):
        self.input_handlers.append(handler)

    def pop_handler(self):
        if self.input_handlers:
            return self.input_handlers.pop()
        return None

    def get_handlers(self):
        return self.input_handlers

    def handle_input(self, input_str):
        if not self.input_handlers:
            raise ValueError("No input handlers available")

        try:
            for handler in reversed(self.input_handlers):
                output, handled = handler.handle_input(input_str)
                if handled:
                    return (output + self.input_handlers[-1].prompt, True)
        except Exception as e:
            return (str(e), False)
        return ("", False)


input_context_handler = InputContextHandler([default_terminal])
