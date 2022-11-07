import sys, os
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QDialog,
    QLabel,
    QScrollBar,
    qApp,
)
import platform

from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush, QWheelEvent
from PyQt5.QtWidgets import (QApplication, QWidget, QInputDialog, QRadioButton,
                             QLineEdit, QDialogButtonBox, QFormLayout)

from PyQt5.uic import loadUiType
from PyQt5.Qsci import QsciScintilla

import lexers
from config import config

import re

FORM_CLASS, _ = loadUiType("ui/main.ui")


class FindInputDialog(QDialog):
    def __init__(self, file_ext, parent=None):
        super().__init__(parent)

        self.text = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.radioChoice1 = QRadioButton(self)
        self.radioChoice1.setText('Find in sequence names')
        self.radioChoice2 = QRadioButton(self)
        self.radioChoice2.setText('Find in DNA sequences')

        if file_ext not in ['fastq', 'fas']:
            self.radioChoice1.hide()
            self.radioChoice2.hide()
        layout = QFormLayout(self)
        layout.addRow("Find:", self.text)
        layout.addWidget(self.radioChoice1)
        layout.addWidget(self.radioChoice2)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return self.text.text(), self.radioChoice1.isChecked(), self.radioChoice2.isChecked()


class SequenceEditor(QMainWindow, FORM_CLASS):
    resized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.setWindowIcon(QIcon("ui/resources/itaxo.png"))
        self.path = "Untitled"
        self.txt = ""
        self.setWindowTitle(os.path.basename(self.path))

        self.setupUi(self)
        self.connectTriggers()

        self.value = 0
        # ScrollBar for lazy loading
        self.scroll = QScrollBar(self)
        scroll_x = 780
        scroll_y = 500
        self.scroll.setGeometry(scroll_x, 60, 20, scroll_y)
        self.scroll.valueChanged.connect(lambda: self.scroll_text())
        self.scroll.setFocusPolicy(Qt.WheelFocus)

        self.find = []
        self.find_pos = []
        self.find_string = ""
        self.find_count = 0

        # Editor
        self.editor.setUtf8(True)
        self.editor.setFont(QFont(config.DEFAULT_FONT, config.FONT_SIZE))
        self.editor.setAutoCompletionSource(QsciScintilla.AcsDocument)

        # self.editor.setMarginType(3, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, 30)
        self.editor.setMarginsForegroundColor(QColor(120, 128, 120))
        self.editor.setMarginLineNumbers(0, True)

        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#e6e6e6"))

        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)
        self.editor.setIndentationGuides(True)
        self.editor.setTabIndents(True)
        self.editor.setAutoIndent(True)

        self.LEXERS = {
            "md": lexers.MarkdownLexer,
            "py": lexers.PythonLexer,
            "txt": lexers.PythonLexer,
            "fa": lexers.FastaLexer,
            "fas": lexers.FastaLexer,
            "fsa": lexers.FastaLexer,
            "fastq": lexers.FastqLexer,
            "nex": lexers.NexusLexer,
            "nxs": lexers.NexusLexer,
            "phy": lexers.PhylipLexer,
        }
        self.setLexer(self.LEXERS["py"])

        # search indicator
        self.SEARCH_INDICATOR_ID = 16
        self.editor.indicatorDefine(QsciScintilla.FullBoxIndicator, self.SEARCH_INDICATOR_ID)
        self.editor.indicatorDefine(QsciScintilla.BoxIndicator, self.SEARCH_INDICATOR_ID + 1)

        # Enable/Disable find_next and find_prev
        self.FIND_ACTIVE = False

        # Keep track of text wrapping
        self.WRAP_MODE = 'unwrapped'

    def wheelEvent(self, event):
        self.scroll.setValue(int(self.value - event.angleDelta().y() / 20))

    def scroll_text(self):
        buffer_text = self.editor.text()
        buffer_arr = buffer_text.split("\n")
        buffer_arr = buffer_arr[:-1]
        buffer_arr = [i + "\n" for i in buffer_arr]
        self.txt[self.value:self.value+(int(self.geometry().height()/20))] = buffer_arr
        self.value = self.scroll.value()
        self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))

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
        self.action_Find.triggered.connect(self.find_search)
        self.action_Find_Prev.triggered.connect(self.find_prev)
        self.action_Find_Next.triggered.connect(self.find_next)
        self.action_Replace.triggered.connect(self.replace)
        # self.action_Find_Down.triggered.connect(self.find_down)
        self.action_About.triggered.connect(self.help_about)
        self.resized.connect(self.ScrollBarPosition)

    # Signal For Screen Size Change
    def resizeEvent(self, event):
        self.resized.emit()
        return super(SequenceEditor, self).resizeEvent(event)

    # Change ScrollBar with screen size
    def ScrollBarPosition(self):
        width = self.geometry().width()
        height = self.geometry().height()
        self.scroll.setGeometry(width-20, 60, 20, height-100)
        value = self.scroll.value()
        self.editor.setText(''.join(self.txt[value:value+(int(self.geometry().height()/20))]))


    def edit_wrap_text(self):
        if self.WRAP_MODE == 'unwrapped':
            self.editor.setWrapMode(QsciScintilla.WrapWord)
            self.WRAP_MODE = 'wrapped'
        else:
            self.editor.setWrapMode(QsciScintilla.WrapNone)
            self.WRAP_MODE = 'unwrapped'

    def find_search(self):
        file_ext = self.path.split(".")[-1]
        dialog = FindInputDialog(file_ext=file_ext)

        outputs = ('', False, False)

        child = dialog.exec_()
        if child == QDialog.Accepted:
            outputs = dialog.getInputs()
        else:
            return

        self.find_string = outputs[0]
        name = outputs[0]
        os_name = platform.system()
        try:
            if os_name == "Linux":
                output = str(subprocess.check_output('grep -n ' + str(name) + ' ' + self.path, shell=True))[2:-1]
            else:
                t_path = self.path
                x = '\"' + t_path.replace("/", "\\") + '\"'
                output = str(subprocess.check_output('findstr /n ' + str(name) + ' ' + x, shell=True))[2:-1]
        except:
            # Not found
            self.dialog_message("Search string not found")
            return
        tmp_x = output.replace("\\r", "").split("\\n")

        if len(tmp_x) == 0:
            # Not found
            self.dialog_message("Search string not found")
            self.FIND_ACTIVE = False
            return

        sequence_names = []
        dna_sequences = []
        pattern_occurances = []

        for i in tmp_x:
            try:
                start = i.split(':')[1]
                if file_ext == 'fastq':
                    if start[0] == '+' or start[0] == '@':
                        sequence_names.append(i)
                elif file_ext == 'fas':
                    if start[0] == '>':
                        sequence_names.append(i)
                    else:
                        dna_sequences.append(i)
                pattern_occurances.append(i)
            except:
                dna_sequences.append(i)
                sequence_names.append(i)
                pattern_occurances.append(i)

        # -1 for text, 0 for sequence names, 1 for dna sequences
        self.search_option = -1

        x = []
        if not outputs[1] and not outputs[2]:
            x += pattern_occurances
        elif outputs[1]:
            self.search_option = 0
            x += sequence_names
        elif outputs[2]:
            self.search_option = 1
            x += dna_sequences
        self.find = [int(i.split(":")[0]) for i in x[:-1]]
        self.find_pos = [int(i.split(":")[1].find(self.find_string)) for i in x[:-1]]

        self.find_count = 0

        self.scroll.setValue(self.find[self.find_count] - 1)
        self.scroll_text()
        current_window_size_max = self.value+(int(self.geometry().height()/20))
        self.clear_highlight_util(current_window_size_max)
        self.find_highlight_util(current_window_size_max)

        self.FIND_ACTIVE = True

    def find_prev(self):
        if not self.FIND_ACTIVE:
            return

        self.find_count = self.find_count - 1
        try:
            self.scroll.setValue(self.find[self.find_count]-1)
            self.value = self.scroll.value()
            self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))
        except:
            self.find_count = len(self.find)-1
            self.scroll.setValue(self.find[self.find_count]-1)
            self.value = self.scroll.value()
            self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))

        current_window_size_max = self.value+(int(self.geometry().height()/20))
        self.clear_highlight_util(current_window_size_max)
        self.find_highlight_util(current_window_size_max)

    def replace(self):
        if not self.FIND_ACTIVE:
            return

        repl, done2 = QInputDialog.getText(
            self, 'Input Dialog', 'Replace:')
        self.txt[self.value] = self.txt[self.value].replace(self.find_string, repl)
        self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))

    def find_next(self):
        if not self.FIND_ACTIVE:
            return

        self.find_count = self.find_count + 1
        try:
            if self.find[self.find_count] >= self.value + int(self.geometry().height() / 20) or \
                    self.find[self.find_count] <= self.value:
                self.scroll.setValue(self.find[self.find_count]-1)
                self.value = self.scroll.value()
                self.editor.setText(''.join(self.txt[self.value:self.value + (int(self.geometry().height()/20))]))
        except:
            self.find_count = 0
            self.scroll.setValue(self.find[self.find_count]-1)
            self.value = self.scroll.value()
            self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))

        current_window_size_max = self.value+(int(self.geometry().height()/20))
        self.clear_highlight_util(current_window_size_max)
        self.find_highlight_util(current_window_size_max)

    def clear_highlight_util(self, window_max):
        self.editor.clearIndicatorRange(min(self.value - 5, 0), 0, window_max+1, 0, self.SEARCH_INDICATOR_ID)
        self.editor.clearIndicatorRange(min(self.value - 5, 0), 0, window_max+1, 0, self.SEARCH_INDICATOR_ID + 1)

    def find_highlight_util(self, window_max):
        offset = 1
        if self.search_option == 0:
            offset = 0

        self.editor.fillIndicatorRange(self.find[self.find_count] - offset - self.value,
                                       self.find_pos[self.find_count],
                                       self.find[self.find_count] - offset - self.value,
                                       self.find_pos[self.find_count] + len(self.find_string),
                                       self.SEARCH_INDICATOR_ID + 1)

        for line in self.find:
            if len([re.finditer(self.find_string, self.txt[line - 1])]):
                self.editor.fillIndicatorRange(line - offset - self.value, 0,
                                               line - offset - self.value + 1, 0,
                                               self.SEARCH_INDICATOR_ID)

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self, caption="Open file", filter=config.FILTER_TYPES
        )
        try:

            #text = open(path , "r").read()
            text = open(path, "r").readlines()
            self.scroll.setMaximum(len(text))
            self.txt = text
            #self.editor.setText(text)
            self.editor.setText(''.join(text[0:(int(self.geometry().height()/20))]))
            self.path = path
            #print(self.path)
            #print(os.path.abspath(__file__))
            self.setWindowTitle(os.path.basename(path))
            self.setLexer(self.LEXERS[path.split(".")[-1]])

        except Exception as e:
            self.dialog_message(str(e))

    def file_save(self):
        if self.path == "Untitled":
            self.file_saveAs()
            return
        self.scroll_text()
        try:
            text = ''.join(self.txt)
            with open(self.path, "w") as f:
                f.write(text)
        except Exception as e:
            self.dialog_message(str(e))

    def file_saveAs(self):
        self.scroll_text()
        path, _ = QFileDialog.getSaveFileName(
            parent=self, caption="Save file as", filter=config.FILTER_TYPES
        )
        text = ''.join(self.txt)

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
