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
        self.setColor(QColor("#444444"), 1)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 1)

        # style for A
        self.setColor(QColor("#4BA619"), 2)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 2)

        # style for T
        self.setColor(QColor("#ff0000"), 3)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 3)

        # style for C
        self.setColor(QColor("#0000ff"), 4)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 4)

        # style for G
        self.setColor(QColor("#C411C7"), 5)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 5)

        self.rules = [
            (re.compile(r"[Aa]", re.MULTILINE), 2),
            (re.compile(r"[Tt]", re.MULTILINE), 3),
            (re.compile(r"[Cc]", re.MULTILINE), 4),
            (re.compile(r"[Gg]", re.MULTILINE), 5),
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


class PhylipLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(PhylipLexer, self).__init__(parent)

        # style 1
        self.setColor(QColor("#639e3b"), 1)  # green
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 1)

        # style 2
        self.setColor(QColor("#f04a3e"), 2)  # blue
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 2)

        # Extract metadata from Phylip files, useful for lexer
        metadata = self.parent().text()[0:100].split('\n')[0].split(' ')

        self.num_species = int(metadata[0])
        self.seq_length = int(metadata[1])

        self.rules = [
            [re.compile(r"^.+ ", re.MULTILINE), 1],
            (re.compile(r'^[0-9]+ [0-9]+$', re.MULTILINE), 2),
        ]

        self.type = None

    def language(self):
        return "Phylip"

    def description(self, style):
        return f"style_{style}"

    def classify_type(self, text):

        """
        Classify Phylip style as:

        1. Strict Sequential (SS)
        2. Strict Interleaved (SI)
        3. Relaxed Sequential (RS)
        4. Relaxed Interleaved (RI)

        """

        self.type = None

        lines = text.strip().split('\n')

        # TODO: handle all text, not just visible on screen

        if len(lines) - 1 == self.num_species:
            # Sequential Format

            # Check for lengths in each sequence
            lengths = [len(line) for line in lines[1:]]

            # Strict must have all lines of equal length, i.e. sequence length + 10
            if all(line == self.seq_length + 10 for line in lengths):
                # Strict Format

                self.type = 'SS'
            else:
                self.type = 'RS'

        print('type', self.type)

    def styleText(self, start, end):

        text = self.parent().text()[start:end]

        phylip_type = self.classify_type(text)

        highlights = []
        for rule in self.rules:
            highlights += [
                (m.start(0), len(bytearray(m.group(0), "utf-8")), rule[1])
                for m in re.finditer(rule[0], text)
            ]

        for highlight in highlights:
            self.startStyling(start + highlight[0])
            self.setStyling(highlight[1], highlight[2])


class NexusLexer(QsciLexerCustom):

    def __init__(self, parent):
        super(NexusLexer, self).__init__(parent)

        # style 1
        self.setColor(QColor("#639e3b"), 1)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 1)

        # style for A
        self.setColor(QColor("#4BA619"), 2)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 2)

        # style for T
        self.setColor(QColor("#ff0000"), 3)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 3)

        # style for C
        self.setColor(QColor("#0000ff"), 4)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 4)

        # style for G
        self.setColor(QColor("#C411C7"), 5)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 5)

        # style for Comments
        self.setColor(QColor("#888888"), 6)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE), 6)

        # style for keywords
        self.setColor(QColor("#5103C1"), 7)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 7)

        # style for keywords
        self.setColor(QColor("#7A1919"), 8)
        self.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE, weight=QFont.Bold), 8)

        self.rules = [
            (re.compile(r"[A]", re.MULTILINE), 2),
            (re.compile(r"[T]", re.MULTILINE), 3),
            (re.compile(r"[C]", re.MULTILINE), 4),
            (re.compile(r"[G]", re.MULTILINE), 5),
            (re.compile(r"[N]", re.MULTILINE), 6),
            (re.compile(r"(#NEXUS|end|;)", re.MULTILINE | re.IGNORECASE), 3),
            (re.compile(r"\=\{?[0-9A-Z_!@#$*?-]+\}?", re.MULTILINE), 2),
            (re.compile(r"^(begin).*;", re.MULTILINE | re.IGNORECASE), 3),
            (re.compile(r"(dimensions|format|matrix|charset|outgroup)", re.MULTILINE | re.IGNORECASE), 7),
            (re.compile(r"(ntax|nchar|datatype|gap|missing|interleave)", re.MULTILINE | re.IGNORECASE), 8),
            (re.compile(r"^\[.*\]", re.MULTILINE), 6),

        ]

    def language(self):
        return "Nexus"

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
