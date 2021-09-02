import sys, os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QDialog,
    QLabel,
    qApp,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.uic import loadUiType
from PyQt5.Qsci import QsciScintilla

import lexers
from config import config

FORM_CLASS, _ = loadUiType("ui/main.ui")


class SequenceEditor(QMainWindow, FORM_CLASS):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.setWindowIcon(QIcon("ui/resources/itaxo.png"))

        self.path = "Untitled"
        self.setWindowTitle(os.path.basename(self.path))

        self.setupUi(self)
        self.connectTriggers()

        # Editor
        self.editor.setUtf8(True)
        self.editor.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE))

        self.editor.setMarginType(1, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(1, 30)
        self.editor.setMarginsForegroundColor(QColor(120, 128, 120))
        self.editor.setMarginLineNumbers(1, True)

        self.LEXERS = {
            "md": lexers.MarkdownLexer,
            "py": lexers.PythonLexer,
            "txt": lexers.PythonLexer,
            "fa": lexers.FastaLexer,
            "fas": lexers.FastaLexer,
            "fsa": lexers.FastaLexer,
            "fastq": lexers.FastqLexer,
            "nex": lexers.PythonLexer,
            "nxs": lexers.PythonLexer,
            "phy": lexers.PythonLexer,
        }
        self.setLexer(self.LEXERS["py"])

    def setLexer(self, lexer):
        self.lexer = lexer(self.editor)
        self.lexer.setDefaultFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE))
        self.editor.setLexer(self.lexer)

    def connectTriggers(self):
        self.action_Open.triggered.connect(self.file_open)
        self.action_Save.triggered.connect(self.file_save)
        self.actionSave_As.triggered.connect(self.file_saveAs)
        self.action_Exit.triggered.connect(qApp.quit)
        self.action_Undo.triggered.connect(self.editor.undo)
        self.action_Redo.triggered.connect(self.editor.redo)
        self.action_Cut.triggered.connect(self.editor.cut)
        self.action_Copy.triggered.connect(self.editor.copy)
        self.action_Paste.triggered.connect(self.editor.paste)
        self.action_Wrap_Text.triggered.connect(self.edit_wrap_text)
        self.action_About.triggered.connect(self.help_about)

    def edit_wrap_text(self):
        if self.editor.WrapMode == QsciScintilla.WrapWord:
            self.editor.setWrapMode(QsciScintilla.WrapNone)
        else:
            self.editor.setWrapMode(QsciScintilla.WrapWord)

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self, caption="Open file", filter=config.FILTER_TYPES
        )
        try:
            text = open(path, "r").read()
            self.editor.setText(text)
            self.path = path
            self.setWindowTitle(os.path.basename(path))
            self.setLexer(self.LEXERS[path.split(".")[-1]])

        except Exception as e:
            self.dialog_message(str(e))

    def file_save(self):
        if self.path == "Untitled":
            self.file_saveAs()
            return

        try:
            text = self.editor.text()
            with open(self.path, "w") as f:
                f.write(text)
        except Exception as e:
            self.dialog_message(str(e))

    def file_saveAs(self):
        path, _ = QFileDialog.getSaveFileName(
            parent=self, caption="Save file as", filter=config.FILTER_TYPES
        )
        text = self.editor.text()

        try:
            with open(path, "w") as f:
                f.write(text)
                self.path = path
                self.setWindowTitle(os.path.basename(path))
                self.setLexer(self.LEXERS[path.split(".")[-1]])

        except Exception as e:
            self.dialog_message(str(e))

    def dialog_message(self, message):
        dlg = QMessageBox(self)
        dlg.setText(message)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def help_about(self):
        mydialog = QDialog()
        mydialog.setWindowTitle("About Us")
        label = QLabel(mydialog)
        label.setText(
            "iTaxotools is a bioinformatic platform designed to facilitate the core work of taxonomists, that is, delimiting, diagnosing and describing species."
        )
        label.adjustSize()
        label.move(100, 60)
        mydialog.setWindowModality(Qt.ApplicationModal)
        mydialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    toolkit = SequenceEditor()
    toolkit.show()
    sys.exit(app.exec_())
