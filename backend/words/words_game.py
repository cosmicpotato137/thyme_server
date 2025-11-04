from terminal.terminal import Terminal, Command, Parameter


class WordsGame(Terminal):
    def __init__(self):
        self.current_word = None
        self.language = None
        self.translation = None

        super().__init__(prompt="")

    def set_game_params(self, language: str, translation: str):
        self.language = language
        self.translation = translation

    
    def get_definition(self)
