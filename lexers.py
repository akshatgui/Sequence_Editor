import re
from config import config

from PyQt5.QtGui import QFont, QColor
from PyQt5.Qsci import QsciLexerPython, QsciLexerMarkdown, QsciLexerCustom


class PythonLexer(QsciLexerPython):
    pass


class MarkdownLexer(QsciLexerMarkdown):
    pass


class FastaLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(FastaLexer, self).__init__(parent)

        # style 1
        self.setColor(QColor("#639e3b"), 1)  # green
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 1)

        self.rules = [
            # From '>' until a newline
            (re.compile(r"^>[^\n]*", re.MULTILINE), 1),  # style 1
        ]

    def language(self):
        return "Fasta"

    def description(self, style):
        return f"style_{style}"

    def styleText(self, start, end):
        text = self.parent().text()[start:end]

        highlights = []
        for rule in self.rules:
            highlights += [
                (m.start(0), len(bytearray(m.group(0), "utf-8")), rule[1])
                for m in re.finditer(rule[0], text)
            ]

        for highlight in highlights:
            self.startStyling(start + highlight[0])
            self.setStyling(highlight[1], highlight[2])


class FastqLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(FastqLexer, self).__init__(parent)

        # style 1
        self.setColor(QColor("#639e3b"), 1)  # green
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 1)

        # style 2
        self.setColor(QColor("#3c8aa7"), 2)  # blue
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 2)

        self.rules = [
            # From '@' until a newline
            (re.compile(r"^@[^\n]*", re.MULTILINE), 1),  # style 1
            # From '+' until a newline
            (re.compile(r"^\+[^\n]*", re.MULTILINE), 2),  # style 2
        ]

    def language(self):
        return "Fastq"

    def description(self, style):
        return f"style_{style}"

    def styleText(self, start, end):

        text = self.parent().text()[start:end]

        highlights = []
        for rule in self.rules:
            highlights += [
                (m.start(0), len(bytearray(m.group(0), "utf-8")), rule[1])
                for m in re.finditer(rule[0], text)
            ]

        for highlight in highlights:
            self.startStyling(start + highlight[0])
            self.setStyling(highlight[1], highlight[2])
