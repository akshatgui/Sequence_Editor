import highlighters

class Config:
    def __init__(self):
        self.FILTER_TYPES = "(*.fas);;(*.fa);;(*.fsa);;(*.fastaq);;(*.nex);;(*.nxs);;(*.phy);;(*.gb);;(*.txt);;(*.py);;(*.md)"
        self.HIGHLIGHTERS = {
            "py": highlighters.PythonHighlighter,
            # "fas": highlighters
        }
        self.EDITOR_STYLE = """QPlainTextEdit{font-family:'Consolas';}"""
        self.FONT_SIZE = 4

config = Config()