# Nama   : Hilya Fitri
# NIM    : F1D02310009
# Kelas  : C

import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import Qt, QSize

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find & Replace")
        self.setFixedWidth(350)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Cari kata...")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Ganti dengan...")

        find_btn = QPushButton("Find Next")
        replace_btn = QPushButton("Replace")
        replace_all_btn = QPushButton("Replace All")

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow("Find:", self.find_input)
        form_layout.addRow("Replace:", self.replace_input)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(find_btn)
        btn_layout.addWidget(replace_btn)
        btn_layout.addWidget(replace_all_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        find_btn.clicked.connect(self.find_next)
        replace_btn.clicked.connect(self.replace)
        replace_all_btn.clicked.connect(self.replace_all)

    def find_next(self):
        text = self.find_input.text()
        if not self.parent().editor.find(text):
            self.parent().editor.moveCursor(QTextCursor.Start)
            self.parent().editor.find(text)

    def replace(self):
        cursor = self.parent().editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        text = self.parent().editor.toPlainText()
        new_text = text.replace(self.find_input.text(), self.replace_input.text())
        self.parent().editor.setPlainText(new_text)

class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Untitled - Notepad")
        self.resize(1000, 700)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.setCentralWidget(self.editor)

        self.file_path = None
        self.is_modified = False

        self.create_actions()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.apply_qss()

        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_status)

    def create_actions(self):
        style = self.style()
        
        self.new_act = QAction(style.standardIcon(QStyle.SP_FileIcon), "New", self)
        self.new_act.setShortcut(QKeySequence.New)
        self.new_act.triggered.connect(self.new_file)

        self.open_act = QAction(style.standardIcon(QStyle.SP_DirOpenIcon), "Open", self)
        self.open_act.setShortcut(QKeySequence.Open)
        self.open_act.triggered.connect(self.open_file)

        self.save_act = QAction(style.standardIcon(QStyle.SP_DialogSaveButton), "Save", self)
        self.save_act.setShortcut(QKeySequence.Save)
        self.save_act.triggered.connect(self.save_file)

        self.cut_act = QAction(style.standardIcon(QStyle.SP_LineEditClearButton), "Cut", self)
        self.cut_act.triggered.connect(self.editor.cut)

        self.copy_act = QAction(style.standardIcon(QStyle.SP_FileDialogDetailedView), "Copy", self)
        self.copy_act.triggered.connect(self.editor.copy)

        self.paste_act = QAction(style.standardIcon(QStyle.SP_FileDialogListView), "Paste", self)
        self.paste_act.triggered.connect(self.editor.paste)

        self.find_act = QAction(style.standardIcon(QStyle.SP_FileDialogContentsView), "Find", self)
        self.find_act.triggered.connect(self.open_find)

    def create_menu(self):
        menubar = self.menuBar()
        #
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction("Save As", self.save_as)

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo", self.editor.undo, QKeySequence.Undo)
        edit_menu.addAction("Redo", self.editor.redo, QKeySequence.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)

        format_menu = menubar.addMenu("Format")
        format_menu.addAction("Font", self.select_font)
        self.wrap_act = QAction("Word Wrap", self, checkable=True)
        self.wrap_act.setChecked(True)
        self.wrap_act.triggered.connect(self.toggle_wrap)
        format_menu.addAction(self.wrap_act)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)

    def create_toolbar(self):
        toolbar = self.addToolBar("Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20)) #
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        toolbar.addAction(self.new_act)
        toolbar.addAction(self.open_act)
        toolbar.addAction(self.save_act)
        toolbar.addSeparator()
        toolbar.addAction(self.cut_act)
        toolbar.addAction(self.copy_act)
        toolbar.addAction(self.paste_act)
        toolbar.addSeparator()
        toolbar.addAction(self.find_act)

    def create_statusbar(self):
        self.left_status = QLabel()
        self.statusBar().addWidget(self.left_status)
        
        self.right_status = QLabel()
        self.statusBar().addPermanentWidget(self.right_status)
        self.update_status()

    def update_status(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        char_count = len(self.editor.toPlainText())
        self.left_status.setText(f" Baris: {line} | Karakter: {char_count} ")
        
        wrap = "ON" if self.editor.lineWrapMode() != QTextEdit.NoWrap else "OFF"
        self.right_status.setText(f" UTF-8 | Word Wrap: {wrap} ")

    def new_file(self):
        if self.confirm_save():
            self.editor.clear()
            self.file_path = None
            self.is_modified = False
            self.update_title()

    def open_file(self):
        if self.confirm_save():
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
            if path:
                with open(path, "r") as f:
                    self.editor.setPlainText(f.read())
                self.file_path = path
                self.is_modified = False
                self.update_title()

    def save_file(self):
        if not self.file_path:
            return self.save_as()
        else:
            with open(self.file_path, "w") as f:
                f.write(self.editor.toPlainText())
            self.is_modified = False
            self.update_title()
            return True

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Text Files (*.txt)")
        if path:
            self.file_path = path
            return self.save_file()
        return False

    def select_font(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self)
        if ok: self.editor.setFont(font)

    def toggle_wrap(self):
        mode = QTextEdit.WidgetWidth if self.wrap_act.isChecked() else QTextEdit.NoWrap
        self.editor.setLineWrapMode(mode)
        self.update_status()

    def open_find(self):
        dialog = FindReplaceDialog(self)
        dialog.exec()

    def show_about(self):
        QMessageBox.about(self, "About", "Notepad Clone v1.0\nHilya Fitri")

    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
        self.update_status()

    def update_title(self):
        title = os.path.basename(self.file_path) if self.file_path else "Untitled"
        if self.is_modified: title += " *"
        self.setWindowTitle(f"{title} - Notepad")

    def confirm_save(self):
        if self.is_modified:
            ret = QMessageBox.question(self, "Konfirmasi", "Simpan perubahan?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if ret == QMessageBox.Yes: return self.save_file()
            return ret == QMessageBox.No
        return True

    def closeEvent(self, event):
        if self.confirm_save(): event.accept()
        else: event.ignore()

    def apply_qss(self):
        #
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QMenuBar { background-color: #2c3e50; color: #ffffff; }
        
            QToolBar { background-color: #ffffff; border-bottom: 1px solid #dcdde1; padding: 4px; }
            QToolButton { 
                color: #000000; 
                font-weight: bold; 
                border: 1px solid #dcdde1; 
                background-color: #f9f9f9; 
                padding: 4px; 
            }
            
            QTextEdit { 
                border: none; 
                background-color: #ffffff; 
                color: #000000; 
                padding: 10px; 
            }
            
            QStatusBar { 
                background-color: #f1f2f6; 
                border-top: 1px solid #dcdde1; 
            }
            QStatusBar QLabel { 
                color: #000000; 
                font-weight: bold;
                padding: 2px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Notepad()
    window.show()
    sys.exit(app.exec())