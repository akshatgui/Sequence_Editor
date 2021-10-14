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

from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtWidgets import QApplication, QWidget

from PyQt5.uic import loadUiType
from PyQt5.Qsci import QsciScintilla

import lexers
from config import config

FORM_CLASS, _ = loadUiType("ui/main.ui")


class SequenceEditor(QMainWindow, FORM_CLASS):
    resized = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.setWindowIcon(QIcon("ui/resources/itaxo.png"))
        #self.showMaximized()
        self.path = "Untitled"
        self.txt = ""
        self.setWindowTitle(os.path.basename(self.path))

        self.setupUi(self)
        self.connectTriggers()

        self.value = 0
        #ScrollBar for lazy loading
        self.scroll = QScrollBar(self)
        scroll_x = 780
        scroll_y = 500
        self.scroll.setGeometry(scroll_x, 60, 20, scroll_y)
        self.scroll.valueChanged.connect(lambda: self.scroll_text())

        

        self.find = []
        self.find_count = 0

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

    def scroll_text(self):
        buffer_text = self.editor.text()
        buffer_arr = buffer_text.split("\n")
        buffer_arr = buffer_arr[:-1]
        buffer_arr = [ i + "\n" for i in buffer_arr]        
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
        self.action_Find.triggered.connect(self.find)
        #self.action_Find_Down.triggered.connect(self.find_down)
        self.action_About.triggered.connect(self.help_about)
        self.resized.connect(self.ScrollBarPosition)


    #Signal For Screen Size Change
    def resizeEvent(self, event):
            self.resized.emit()
            return super(SequenceEditor, self).resizeEvent(event)

    #Change ScrollBar with screen size
    def ScrollBarPosition(self):
        width = self.geometry().width()
        height = self.geometry().height()
        self.scroll.setGeometry(width-20, 60, 20, height-100)
        value = self.scroll.value()
        self.editor.setText(''.join(self.txt[value:value+(int(self.geometry().height()/20))]))
        

    def edit_wrap_text(self):
        if self.editor.WrapMode == QsciScintilla.WrapWord:
            self.editor.setWrapMode(QsciScintilla.WrapNone)
        else:
            self.editor.setWrapMode(QsciScintilla.WrapWord)

    
    

    def find(self):
        if not (self.find):
    
            output = str(subprocess.check_output('findstr /n "sys.arg" .\main.py', shell=True))[2:-1]
            x = output.split("\\r\\n") 
            BL = [i.split(":")[0] for i in x][:-1]
            self.find = [int(i) for i in BL]

            buffer_text = self.editor.text()
            buffer_arr = buffer_text.split("\n")
            buffer_arr = buffer_arr[:-1]
            buffer_arr = [ i + "\n" for i in buffer_arr]        
            self.txt[self.value:self.value+(int(self.geometry().height()/20))] = buffer_arr

            self.scroll.setValue(self.find[self.find_count]-1)
            self.value = self.scroll.value()
            print(self.value)
            self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))

        else:
            self.find_count = self.find_count + 1
            try:
                self.scroll.setValue(self.find[self.find_count]-1)
                self.value = self.scroll.value()
                print(self.value)
                self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))
            except:
                self.find_count = 0
                self.scroll.setValue(self.find[self.find_count]-1)
                self.value = self.scroll.value()
                self.editor.setText(''.join(self.txt[self.value:self.value+(int(self.geometry().height()/20))]))




    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self, caption="Open file", filter=config.FILTER_TYPES
        )
        try:
            
            #text = open(path , "r").read()
            text = open(path , "r").readlines()
            self.scroll.setMaximum(len(text))            
            self.txt = text
            #self.editor.setText(text)
            self.editor.setText(''.join(text[0:(int(self.geometry().height()/20))]))
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
