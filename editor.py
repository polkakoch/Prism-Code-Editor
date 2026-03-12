import os, json
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QFileSystemModel, QTreeView,
    QSplitter, QAction, QFileDialog, QInputDialog, QMenu,
    QLabel, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QCompleter, QTabWidget
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QTextFormat
from PyQt5.QtCore import Qt, QTimer, QFileInfo
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt5.QtCore import QRegExp



SETTINGS_FILE = "settings.json"


class LanguageHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language="python"):
        super().__init__(document)
        self.highlighting_rules = []
        self.language = language

        def format(color, style=''):
            _format = QTextCharFormat()
            _format.setForeground(QColor(color))
            if 'bold' in style:
                _format.setFontWeight(QFont.Bold)
            if 'italic' in style:
                _format.setFontItalic(True)
            return _format

        colors = {
            "keyword": "#569CD6",
            "builtin": "#C586C0",
            "number": "#B5CEA8",
            "string": "#CE9178",
            "comment": "#6A9955",
            "defclass": "#DCDCAA",
            "operator": "#D4D4D4",
            "identifier": "#9CDCFE"
        }

        if language == "python":
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

        else:  # JavaScript / TypeScript-like
            keywords = [
                'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
                'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
                'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
                'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
                'void', 'while', 'with', 'yield', 'async', 'await'
            ]

            builtins = [
                'Array', 'Boolean', 'Date', 'Error', 'Function', 'JSON', 'Math',
                'Number', 'Object', 'RegExp', 'String', 'Promise', 'Map', 'Set',
                'console', 'window', 'document'
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

        if language == "python":
            self.highlighting_rules.append((QRegExp(r'#.*'), format(colors["comment"], 'italic')))
            self.highlighting_rules.append((QRegExp(r'\bdef\b\s*(\w+)'), format(colors["defclass"], 'bold')))
            self.highlighting_rules.append((QRegExp(r'\bclass\b\s*(\w+)'), format(colors["defclass"], 'bold')))
        else:
            self.highlighting_rules.append((QRegExp(r'//.*'), format(colors["comment"], 'italic')))
            self.highlighting_rules.append((QRegExp(r'/\*.*\*/'), format(colors["comment"], 'italic')))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

class CodeEditor(QMainWindow):
    def __init__(self, project_path, project_type="python"):
        super().__init__()
        self.project_path = project_path
        self.project_type = project_type
        self.current_file = None
        self.snippets = self.load_python_snippets()
        self.pending_completion = None

     
        self.settings = self.load_settings()
        self.lang = self.settings.get("language", "ru")
        self.theme = self.settings.get("theme", "dark")

        self.LANG = {
            "ru": {
                "title": "Редактор — Prism Code Editor",
                "create_file": "Создать файл",
                "delete_file": "Удалить",
                "rename_file": "Переименовать",
                "save_msg": "Файл сохранён",
                "open": "Открыть файл",
                "new_file_prompt": "Введите имя файла (с расширением):",
                "rename_file_prompt": "Введите новое имя файла:",
            },
            "en": {
                "title": "Editor — Prism Code Editor",
                "create_file": "Create File",
                "delete_file": "Delete",
                "rename_file": "Rename",
                "save_msg": "File saved",
                "open": "Open File",
                "new_file_prompt": "Enter file name (with extension):",
                "rename_file_prompt": "Enter new file name:",
            }
        }

        self.init_ui()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"language": "ru", "theme": "dark_blue.xml"}

    def load_python_snippets(self):
        path = os.path.join(os.path.dirname(__file__), "snippets_python.json")
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return {}
        return {item.get("prefix"): item.get("body", "") for item in data if "prefix" in item}

    def init_ui(self):
        self.setWindowTitle(self.LANG[self.lang]["title"])
        self.resize(1000, 600)

        # Определяем, светлая или тёмная тема, по названию qt_material
        if str(self.theme).startswith("light"):
            bg = "#ffffff"
            fg = "#1e1e1e"
        else:
            bg = "#1e1e1e"
            fg = "#d4d4d4"

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg};
                color: {fg};
                font-family: Consolas, 'Fira Code', monospace;
                font-size: 13px;
            }}
        """)

        # Модель файлов и дерево (панель проводника)
        self.model = QFileSystemModel()
        self.model.setRootPath(self.project_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.project_path))
        self.tree.setColumnWidth(0, 200)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.doubleClicked.connect(self.open_file_from_tree)
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                border: none;
                show-decoration-selected: 1;
            }
            QTreeView::item {
                height: 20px;
                padding: 2px 6px;
            }
            QTreeView::item:selected {
                background-color: #094771;
            }
        """)

        # Заголовок "EXPLORER" над деревом, как в VS Code
        explorer_header = QLabel("EXPLORER")
        explorer_header.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                padding: 4px 8px;
                background-color: #252526;
                border-bottom: 1px solid #2d2d2d;
            }
        """)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(explorer_header)
        left_layout.addWidget(self.tree)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border-right: 1px solid #2d2d2d;
            }
        """)

        # Область редактора с вкладками файлов (одна широкая панель с крестиком)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d4d4d4;
                padding: 6px 26px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
            QTabBar::close-button {
                image: url(:/qt-project.org/styles/commonstyle/images/close-16.png);
                subcontrol-position: right;
                margin-left: 4px;
            }
        """)

        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.tab_widget)

        # Основной сплиттер между проводником и редактором
        splitter = QSplitter()
        splitter.addWidget(left_panel)
        splitter.addWidget(editor_panel)
        splitter.setSizes([260, 740])

        # Простое автодополнение (Ctrl+Space) на основе ключевых слов
        self.completion_words = list(set(
            [
                # Python
                'def', 'class', 'import', 'from', 'return', 'for', 'while', 'if', 'elif', 'else',
                'with', 'as', 'try', 'except', 'finally', 'True', 'False', 'None', 'print',
                # JavaScript
                'function', 'const', 'let', 'var', 'async', 'await', 'return', 'class',
                'console', 'log', 'document', 'window'
            ]
        ))
        self.completer = QCompleter(self.completion_words, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

        # Для простого автодополнения часто используемых слов
        self.common_python_words = [
            'print', 'import', 'from', 'class', 'def', 'return', 'for', 'while', 'if', 'elif', 'else',
            'with', 'as', 'try', 'except', 'finally'
        ]


        # Нижняя строка состояния
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding: 0 8px;
            }
        """)

        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
        """)
        self.setCentralWidget(splitter)
        self.statusBar().addWidget(self.status_label)

      
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        self.addAction(save_action)

        complete_action = QAction("Complete", self)
        complete_action.setShortcut("Ctrl+Space")
        complete_action.triggered.connect(self.trigger_completion)
        self.addAction(complete_action)

        # Стартовая пустая вкладка
        self.add_tab(None, "")

    def eventFilter(self, obj, event):
        # Обработка автодополнения и сниппетов только для QTextEdit
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QKeyEvent
        from PyQt5.QtWidgets import QToolTip

        if isinstance(obj, QTextEdit) and event.type() == QEvent.KeyPress:
            key_event = event  # type: QKeyEvent
            lang = obj.property("language") or "python"

            # Для Python: показываем простое автодополнение часто используемых конструкций
            if lang == "python":
                # Вводимый символ
                text = key_event.text()

                # Обновляем подсказку при наборе букв/символов
                if text and not key_event.key() in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
                    cursor = obj.textCursor()
                    cursor.select(cursor.WordUnderCursor)
                    word = cursor.selectedText()
                    if word:
                        # Ищем подходящее слово по префиксу
                        suggestion = None
                        for w in self.common_python_words:
                            if w.startswith(word) and w != word:
                                suggestion = w
                                break
                        self.pending_completion = suggestion

                        if suggestion:
                            pos = obj.mapToGlobal(obj.cursorRect().bottomRight())
                            QToolTip.showText(pos, suggestion, obj)
                        else:
                            QToolTip.hideText()

                # Нажатие Tab: подтверждаем автодополнение или разворачиваем сниппет
                if key_event.key() == Qt.Key_Tab:
                    cursor = obj.textCursor()
                    cursor.select(cursor.WordUnderCursor)
                    word = cursor.selectedText()

                    # Сначала — простое автодополнение часто используемых слов
                    if self.pending_completion:
                        cursor.insertText(self.pending_completion)
                        self.pending_completion = None
                        QToolTip.hideText()
                        return True

                    # Если нет pending_completion — пробуем сниппет (main, class и т.п.)
                    if word in self.snippets:
                        body = self.snippets[word]
                        cursor.insertText(body)
                        return True

        return super().eventFilter(obj, event)

    def add_tab(self, file_path, content):
        editor = QTextEdit()
        editor.setFont(QFont("Consolas", 11))
        editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 8px;
            }
        """)
        if content:
            editor.setText(content)

        # Определяем язык подсветки
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".py":
                lang = "python"
            elif ext in (".js", ".ts", ".jsx"):
                lang = "javascript"
            else:
                lang = "python" if self.project_type in ("python", "django") else "javascript"
        else:
            lang = "python" if self.project_type in ("python", "django") else "javascript"

        # Привязываем хайлайтер к редактору
        editor._highlighter = LanguageHighlighter(editor.document(), lang)

        # Сохраняем путь файла и язык в свойства редактора
        editor.setProperty("file_path", file_path)
        editor.setProperty("language", lang)
        editor.installEventFilter(self)

        tab_title = os.path.basename(file_path) if file_path else "Untitled"
        idx = self.tab_widget.addTab(editor, tab_title)
        self.tab_widget.setCurrentIndex(idx)
        self.current_file = file_path

        return editor

    def current_editor(self):
        return self.tab_widget.currentWidget()

    def on_tab_changed(self, index):
        editor = self.tab_widget.widget(index)
        if editor is None:
            self.current_file = None
        else:
            self.current_file = editor.property("file_path")

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget is not None:
            self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.current_file = None
            # Можно создать новую пустую вкладку
            self.add_tab(None, "")

    def open_file_from_tree(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            # Проверяем, не открыт ли уже этот файл
            for i in range(self.tab_widget.count()):
                ed = self.tab_widget.widget(i)
                if ed and ed.property("file_path") == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            self.add_tab(file_path, content)

    def save_file(self):
        editor = self.current_editor()
        if editor is None:
            return
        file_path = editor.property("file_path")
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(editor.toPlainText())
        self.show_temp_message(self.LANG[self.lang]["save_msg"])

    def trigger_completion(self):
        editor = self.current_editor()
        if editor is None:
            return
        cursor = editor.textCursor()
        cursor.select(cursor.WordUnderCursor)
        prefix = cursor.selectedText()
        if not prefix:
            return
        self.completer.setCompletionPrefix(prefix)
        self.completer.setWidget(editor)
        cr = editor.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                    self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def show_temp_message(self, text, timeout=2000):
        self.status_label.setText(text)
        QTimer.singleShot(timeout, lambda: self.status_label.setText(""))

    
    def show_context_menu(self, pos):
        menu = QMenu()
        create_action = QAction(self.LANG[self.lang]["create_file"], self)
        delete_action = QAction(self.LANG[self.lang]["delete_file"], self)
        rename_action = QAction(self.LANG[self.lang]["rename_file"], self)
        menu.addAction(create_action)
        menu.addAction(delete_action)
        menu.addAction(rename_action)

        create_action.triggered.connect(self.create_file)
        delete_action.triggered.connect(self.delete_file)
        rename_action.triggered.connect(self.rename_file)

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

    def rename_file(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return

        old_path = self.model.filePath(index)
        base_dir = os.path.dirname(old_path)
        old_name = os.path.basename(old_path)

        new_name, ok = QInputDialog.getText(
            self,
            self.LANG[self.lang]["rename_file"],
            self.LANG[self.lang]["rename_file_prompt"],
            text=old_name
        )
        if not ok or not new_name:
            return

        new_path = os.path.join(base_dir, new_name)
        if new_path == old_path:
            return

        try:
            os.rename(old_path, new_path)
        except OSError:
            return

        # Обновляем текущий файл, если он был открыт
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if ed and ed.property("file_path") == old_path:
                ed.setProperty("file_path", new_path)
                self.tab_widget.setTabText(i, os.path.basename(new_path))
                if self.current_editor() is ed:
                    self.current_file = new_path

        self.model.layoutChanged.emit()
