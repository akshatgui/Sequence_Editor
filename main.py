import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QPlainTextEdit, QStatusBar, QToolBar, QVBoxLayout, QAction, QFileDialog, QMessageBox,QDialog
from PyQt5.QtCore import Qt, QSize                 
from PyQt5.QtGui import QFontDatabase, QIcon, QKeySequence,QPixmap
from PyQt5.QtPrintSupport import QPrintDialog
import syntax_pars


class AppDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Text Editor')
        self.setWindowIcon(QIcon('./icon/text.jpg'))
        self.screen_width, self.screen_height = self.geometry().width, self.geometry().height()
        
               

        self.filterTypes = '(*.fas);;(*.fa);;(*.fsa);;(*.fastaq);;(*.nex);;(*.nxs);;(*.phy);;(*.gb);;Text Document (*.txt);; Python (*.py);; Markdown (*.md)'
        self.path = None

        fixedFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedFont.setPointSize(10)

        mainLayout = QVBoxLayout()

        self.editor = QPlainTextEdit()
        
        
        mainLayout.addWidget(self.editor)


        self.statusBar = self.statusBar()


        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)


        file_menu = self.menuBar().addMenu('&File')

        #Toolbar

        
        file_toolbar = QToolBar('File')
        file_toolbar.setIconSize(QSize(60, 60))
        self.addToolBar(Qt.BottomToolBarArea, file_toolbar)

        open_file_action = QAction(QIcon('./icon/open.jpg'), 'Open File...', self)
        open_file_action.setStatusTip('Open file')
        open_file_action.setShortcut(QKeySequence.Open)
        open_file_action.triggered.connect(self.file_open)


        save_file_action = self.create_action(self, './icon/save.png', 'Save File', 'Save file', self.file_save)
        save_file_action.setShortcut(QKeySequence.Save)

        save_fileAs_action = self.create_action(self, './icon/saveAs.png', 'Save File As...', 'Save file as', self.file_saveAs)
        save_fileAs_action.setShortcut(QKeySequence('Ctrl+Shift+S'))


        file_menu.addActions([open_file_action, save_file_action, save_fileAs_action])
        file_toolbar.addActions([open_file_action, save_file_action, save_fileAs_action])

        
        edit_menu = self.menuBar().addMenu('&Edit')
        edit_toolbar =QToolBar('Edit')
        edit_toolbar.setIconSize(QSize(60, 60))
        self.addToolBar(Qt.BottomToolBarArea, edit_toolbar)

        undo_action = self.create_action(self, './icon/undo.png', 'Undo', 'Undo', self.editor.undo)
        undo_action.setShortcut(QKeySequence.Undo)

        redo_action = self.create_action(self, './icon/redo.png', 'Redo', 'Redo', self.editor.redo)
        redo_action.setShortcut(QKeySequence.Redo)

        edit_menu.addActions([undo_action, redo_action])
        edit_toolbar.addActions([undo_action, redo_action])

        edit_menu.addSeparator()
        edit_toolbar.addSeparator()


        wrap_text_action = self.create_action(self, './icon/wrap.png', 'Wrap Text', 'Wrap text', self.toggle_wrap_text)
        wrap_text_action.setShortcut('Ctrl+Shift+W')
        edit_menu.addAction(wrap_text_action)
        edit_toolbar.addAction(wrap_text_action)

        edit_menu.addSeparator()
        edit_toolbar.addSeparator()

        icon_action = self.create_action(self, './icon/itaxo.jpeg', 'About', 'About',self.openAbout )
        edit_toolbar.addAction(icon_action)

        self.showMaximized()

        

        self.update_title()

        #Syntax Highlighter
        self.editor.setStyleSheet("""QPlainTextEdit{
	            font-family:'Consolas'; 
	            color: #ccc; 
	            background-color: #2b2b2b;}""")
        self.highlight = syntax_pars.PythonHighlighter(self.editor.document())



        self.show()

    def toggle_wrap_text(self):
        self.editor.setLineWrapMode(not self.editor.lineWrapMode())


        self.update_title()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open file',
            directory='',
            filter=self.filterTypes
        )

        if path:
            try:    
                with open(path, 'r') as f:
                    text = f.read()
                    f.close()
            except Exception as e:
                self.dialog_message(str(e))
            else:
                self.path = path
                self.editor.setPlainText(text)
                self.update_title()




    def file_save(self):
        if self.path is None:
            self.file_saveAs()
        else:
            try:
                text = self.editor.toPlainText()
                with open(self.path, 'w') as f:
                    f.write(text)
                    f.close()
            except Exception as e:  
                self.dialog_message(str(e))

    def file_saveAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            'Save file as',
            '',
            self.filterTypes
        )                               

        text = self.editor.toPlainText()

        if not path:
            return
        else:
            try:
                with open(path, 'w') as f:
                    f.write(text)
                    f.close()
            except Exception as e:
                self.dialog_message(str(e))
            else:
                self.path = path
                self.update_title()
    

    def update_title(self):
        self.setWindowTitle('{0} - Editor'.format(os.path.basename(self.path) if self.path else 'Untitled'))

    def dialog_message(self, message):
        dlg = QMessageBox(self)
        dlg.setText(message)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def create_action(self, parent, icon_path, action_name, set_status_tip, triggered_method)   :
        action = QAction(QIcon(icon_path), action_name, parent)
        action.setStatusTip(set_status_tip)
        action.triggered.connect(triggered_method)
        return action


    def openAbout(self):
        mydialog = QDialog()
        mydialog.setWindowTitle("About Us")
        label = QLabel(mydialog)
        label.setText("iTaxotools is a bioinformatic platform designed to facilitate the core work of taxonomists, that is, delimiting, diagnosing and describing species.")
        label.adjustSize()
        label.move(100, 60)
        mydialog.setWindowModality(Qt.ApplicationModal)
        mydialog.exec()



app = QApplication(sys.argv)
toolkit = AppDemo()
toolkit.show()
sys.exit(app.exec_())