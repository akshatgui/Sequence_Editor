import sys, os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QFontDatabase, QIcon
from config import config

from PyQt5.uic import loadUiType

FORM_CLASS, _ = loadUiType("ui/main.ui")

class SequenceEditor(QMainWindow, FORM_CLASS):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.setWindowIcon(QIcon("ui/resources/itaxo.jpeg"))

        self.path = "Untitled"

        self.setupUi(self)
        self.connectTriggers()


        fixedFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedFont.setPointSize(config.FONT_SIZE)

        # Syntax Highlighter
        self.editor.setStyleSheet(config.EDITOR_STYLE)
        self.highlighter = config.HIGHLIGHTERS['py'](self.editor.document())

    def connectTriggers(self):
        self.action_Open.triggered.connect(self.file_open)
        self.action_Save.triggered.connect(self.file_save)
        self.actionSave_As.triggered.connect(self.file_saveAs)
        self.action_Undo.triggered.connect(self.editor.undo)
        self.action_Redo.triggered.connect(self.editor.redo)
        self.action_Cut.triggered.connect(self.editor.cut)
        self.action_Copy.triggered.connect(self.editor.copy)
        self.action_Paste.triggered.connect(self.editor.paste)
        self.action_Wrap_Text.triggered.connect(self.edit_wrap_text)

    def edit_wrap_text(self):
        self.editor.setLineWrapMode(not self.editor.lineWrapMode())

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self, caption="Open file", filter=config.FILTER_TYPES
        )

        try:
            text = open(path, "r").read()
            self.editor.setPlainText(text)
            self.path = path
            self.setWindowTitle(os.path.basename(path))
            self.highlighter = config.HIGHLIGHTERS[path.split('.')[-1]](self.editor.document())

        except Exception as e:
            self.dialog_message(str(e))
                

    def file_save(self):
        if self.path == 'Untitled':
            self.file_saveAs()
            return

        try:
            text = self.editor.toPlainText()
            with open(self.path, "w") as f:
                f.write(text)
        except Exception as e:
            self.dialog_message(str(e))

    def file_saveAs(self):
        path, _ = QFileDialog.getSaveFileName(
            parent=self, caption="Save file as", filter=config.FILTER_TYPES
        )
        text = self.editor.toPlainText()

        try:
            with open(path, "w") as f:
                f.write(text)
                self.path = path
                self.setWindowTitle(os.path.basename(path))
                self.highlighter = config.HIGHLIGHTERS[path.split('.')[-1]](self.editor.document())
                
        except Exception as e:
            self.dialog_message(str(e))

    def dialog_message(self, message):
        dlg = QMessageBox(self)
        dlg.setText(message)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    # def openAbout(self):
    #     mydialog = QDialog()
    #     mydialog.setWindowTitle("About Us")
    #     label = QLabel(mydialog)
    #     label.setText(
    #         "iTaxotools is a bioinformatic platform designed to facilitate the core work of taxonomists, that is, delimiting, diagnosing and describing species."
    #     )
    #     label.adjustSize()
    #     label.move(100, 60)
    #     mydialog.setWindowModality(Qt.ApplicationModal)
    #     mydialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    toolkit = SequenceEditor()
    toolkit.show()
    sys.exit(app.exec_())
