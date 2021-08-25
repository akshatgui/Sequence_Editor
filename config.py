import highlighters


class Config:
    def __init__(self):
        self.FILTER_TYPES = "(*.fas);;(*.fa);;(*.fsa);;(*.fastq);;(*.nex);;(*.nxs);;(*.phy);;(*.gb);;(*.txt);;(*.py);;(*.md)"
        self.HIGHLIGHTERS = {
            "nex": highlighters.NexHighlighter,
            "nxs": highlighters.NexHighlighter,
            "py": highlighters.PythonHighlighter,
            "txt": highlighters.PythonHighlighter,
            "md": highlighters.PythonHighlighter,
            "gb": highlighters.PythonHighlighter,
            "phy": highlighters.PythonHighlighter,
            "fas": highlighters.FasHighlighter,
            "fa": highlighters.FasHighlighter,
            "fsa": highlighters.FasHighlighter,
            "fastq": highlighters.FastqHighlighter,
        }
        self.EDITOR_STYLE = """QPlainTextEdit{font-family:'Consolas';}"""
        self.FONT_SIZE = 4


config = Config()
