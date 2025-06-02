class InputHandler:
    def __init__(self, prompt: str):
        self.prompt = prompt

    def handle_input(self, input: str):
        """
        Handle the input string. This method should be overridden by subclasses.
        Returns True if the input was handled, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement this method")

    pass
