import os, json
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QFileSystemModel, QTreeView,
    QSplitter, QAction, QFileDialog, QInputDialog, QMenu, QLabel, QApplication
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QTextFormat
from PyQt5.QtCore import Qt, QTimer, QFileInfo
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt5.QtCore import QRegExp



SETTINGS_FILE = "settings.json"


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        def format(color, style=''):
            _format = QTextCharFormat()
            _format.setForeground(QColor(color))
            if 'bold' in style:
                _format.setFontWeight(QFont.Bold)
            if 'italic' in style:
                _format.setFontItalic(True)
            return _format

       
        colors = {
            "keyword": "#9CDCFE",    
            "builtin": "#C586C0",     
            "number": "#B5CEA8",      
            "string": "#CE9178",      
            "comment": "#6A9955",     
            "defclass": "#DCDCAA",    
            "operator": "#D4D4D4",  
            "identifier": "#9CDCFE" 
        }

       
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]

        builtins = [
            'abs', 'dict', 'help', 'min', 'setattr',
            'all', 'dir', 'hex', 'next', 'slice', 'any', 'divmod', 'id',
            'object', 'sorted', 'ascii', 'enumerate', 'input', 'oct', 'staticmethod',
            'bin', 'eval', 'int', 'open', 'str', 'bool', 'exec', 'isinstance',
            'ord', 'sum', 'bytearray', 'filter', 'issubclass', 'pow', 'super',
            'bytes', 'float', 'iter', 'print', 'tuple', 'callable', 'format',
            'len', 'property', 'type', 'chr', 'frozenset', 'list', 'range',
            'vars', 'classmethod', 'getattr', 'locals', 'repr', 'zip', 'compile',
            'globals', 'map', 'reversed', '__import__'
        ]

        
        for word in keywords:
            pattern = QRegExp(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, format(colors["keyword"], 'bold')))

        
        for word in builtins:
            pattern = QRegExp(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, format(colors["builtin"])))

      
        self.highlighting_rules.append((QRegExp(r'\b[0-9]+\b'), format(colors["number"])))

      
        self.highlighting_rules.append((QRegExp(r'".*"'), format(colors["string"])))
        self.highlighting_rules.append((QRegExp(r"'.*'"), format(colors["string"])))

        
        self.highlighting_rules.append((QRegExp(r'#.*'), format(colors["comment"], 'italic')))

        
        self.highlighting_rules.append((QRegExp(r'\bdef\b\s*(\w+)'), format(colors["defclass"], 'bold')))
        self.highlighting_rules.append((QRegExp(r'\bclass\b\s*(\w+)'), format(colors["defclass"], 'bold')))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

class CodeEditor(QMainWindow):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.current_file = None

     
        self.settings = self.load_settings()
        self.lang = self.settings.get("language", "ru")

        self.LANG = {
            "ru": {
                "title": "Редактор — Prism Code Editor",
                "create_file": "Создать файл",
                "delete_file": "Удалить",
                "save_msg": "Файл сохранён",
                "open": "Открыть файл",
                "new_file_prompt": "Введите имя файла (с расширением):",
            },
            "en": {
                "title": "Editor — Prism Code Editor",
                "create_file": "Create File",
                "delete_file": "Delete",
                "save_msg": "File saved",
                "open": "Open File",
                "new_file_prompt": "Enter file name (with extension):",
            }
        }

        self.init_ui()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"language": "ru"}

    def init_ui(self):
        self.setWindowTitle(self.LANG[self.lang]["title"])
        self.resize(1000, 600)

 
        self.model = QFileSystemModel()
        self.model.setRootPath(self.project_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.project_path))
        self.tree.setColumnWidth(0, 200)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.doubleClicked.connect(self.open_file_from_tree)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.highlighter = PythonHighlighter(self.editor.document())


        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00ff99; font-weight: bold;")

        
        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.editor)
        splitter.setSizes([250, 750])

        self.setCentralWidget(splitter)
        self.statusBar().addWidget(self.status_label)

      
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        self.addAction(save_action)

   
    def open_file_from_tree(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                self.editor.setText(f.read())
            self.current_file = file_path

    def save_file(self):
        if not self.current_file:
            return
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self.show_temp_message(self.LANG[self.lang]["save_msg"])

    def show_temp_message(self, text, timeout=2000):
        self.status_label.setText(text)
        QTimer.singleShot(timeout, lambda: self.status_label.setText(""))

    
    def show_context_menu(self, pos):
        menu = QMenu()
        create_action = QAction(self.LANG[self.lang]["create_file"], self)
        delete_action = QAction(self.LANG[self.lang]["delete_file"], self)
        menu.addAction(create_action)
        menu.addAction(delete_action)

        create_action.triggered.connect(self.create_file)
        delete_action.triggered.connect(self.delete_file)

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def create_file(self):
        name, ok = QInputDialog.getText(self, self.LANG[self.lang]["create_file"], self.LANG[self.lang]["new_file_prompt"])
        if ok and name:
            new_path = os.path.join(self.project_path, name)
            if not os.path.exists(new_path):
                with open(new_path, "w", encoding="utf-8"):
                    pass
                self.model.layoutChanged.emit()

    def delete_file(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if os.path.isfile(path):
            os.remove(path)
            self.model.layoutChanged.emit()
        elif os.path.isdir(path):
            os.rmdir(path)
            self.model.layoutChanged.emit()
