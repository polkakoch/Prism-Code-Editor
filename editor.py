import importlib.util
import json
import os
import sqlite3
import sys
import time
from datetime import datetime

from PyQt5.QtCore import QDateTime, QDir, QProcess, QRegExp, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QKeySequence, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import (
    QAction,
    QColorDialog,
    QComboBox,
    QDateTimeEdit,
    QFileDialog,
    QFileSystemModel,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QShortcut,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
PLUGINS_DIR = os.path.join(APP_DIR, "plugins")


DEFAULT_SETTINGS = {
    "theme": "dark",
    "language": "ru",
    "accent_color": "#0e639c",
    "background_color": "#1e1f22",
    "side_color": "#18191c",
    "panel_color": "#202124",
    "editor_color": "#1e1f22",
    "terminal_color": "#111214",
    "text_color": "#d6d6d6",
    "font_family": "Consolas",
    "font_size": 14,
    "background_image": "",
    "last_project": "",
    "recent_projects": [],
}


def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                settings.update(json.load(file))
        except (OSError, json.JSONDecodeError):     
            pass
    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=2)


def color_shift(hex_color, amount):
    color = QColor(hex_color)
    if amount > 0:
        color = color.lighter(100 + amount)
    else:
        color = color.darker(100 - amount)
    return color.name()


def setting_color(settings, key, fallback):
    value = settings.get(key, fallback)
    return QColor(value).name() if QColor(value).isValid() else fallback


def css_image_url(path):
    if not path:
        return ""
    return path.replace("\\", "/")


def build_style(settings):
    accent = setting_color(settings, "accent_color", "#0e639c")
    theme = settings.get("theme", "dark")
    font_family = settings.get("font_family", "Consolas")
    font_size = int(settings.get("font_size", 14))

    if theme == "light":
        bg = "#f4f5f7"
        side = "#eceef2"
        panel = "#ffffff"
        text = "#202327"
        muted = "#6b7280"
        border = "#d8dde6"
        editor_bg = "#ffffff"
        tab = "#eef1f6"
        input_bg = "#ffffff"
        terminal_bg = "#f8fafc"
    else:
        bg = "#1e1f22"
        side = "#18191c"
        panel = "#202124"
        text = "#d6d6d6"
        muted = "#9da1aa"
        border = "#32353d"
        editor_bg = "#1e1f22"
        tab = "#25262b"
        input_bg = "#25262b"
        terminal_bg = "#111214"

    bg = setting_color(settings, "background_color", bg)
    side = setting_color(settings, "side_color", side)
    panel = setting_color(settings, "panel_color", panel)
    editor_bg = setting_color(settings, "editor_color", editor_bg)
    terminal_bg = setting_color(settings, "terminal_color", terminal_bg)
    text = setting_color(settings, "text_color", text)

    accent_hover = color_shift(accent, 18)
    accent_down = color_shift(accent, -18)
    background_image = css_image_url(settings.get("background_image", ""))
    image_rule = f'border-image: url("{background_image}") 0 0 0 0 stretch stretch;' if background_image else ""

    return f"""
    QMainWindow, QWidget {{
        background: {bg};
        color: {text};
        font-family: "Segoe UI", Arial;
        font-size: 13px;
    }}
    #ActivityBar {{ background: {side}; }}
    #SidePanel, #TopBar {{ background: {panel}; border: none; }}
    #MainEditor, #EditorSurface {{
        background: {bg};
        {image_rule}
    }}
    #MenuButton {{
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: 400;
    }}
    #MenuButton:hover {{
        background: {tab};
        color: {text};
        border: none;
    }}
    #CommandSearch {{
        border-radius: 5px;
        min-height: 20px;
        padding: 3px 10px;
    }}
    #WindowChromeLabel {{
        font-size: 14px;
        font-weight: 700;
        padding: 0 8px 0 2px;
        color: {accent};
    }}
    QWidget#WorkspacePage {{
        background: transparent;
    }}
    QPushButton {{
        background: {tab};
        border: 1px solid {border};
        border-radius: 5px;
        color: {text};
        padding: 7px 11px;
    }}
    QPushButton:hover {{ background: {accent_hover}; color: white; border-color: {accent_hover}; }}
    QPushButton:pressed {{ background: {accent_down}; }}
    QPushButton[active="true"], QPushButton#PrimaryButton {{
        background: {accent};
        border-color: {accent};
        color: white;
        font-weight: 600;
    }}
    QPushButton#ActivityButton {{
        border: none;
        border-radius: 6px;
        padding: 0;
        font-size: 11px;
    }}
    QMenu {{
        background: {panel};
        color: {text};
        border: 1px solid {border};
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 28px 6px 18px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background: {accent};
        color: white;
    }}
    QLineEdit, QPlainTextEdit, QComboBox, QDateTimeEdit, QSpinBox {{
        background: {input_bg};
        border: 1px solid {border};
        border-radius: 5px;
        color: {text};
        padding: 6px;
        selection-background-color: {accent};
    }}
    QPlainTextEdit {{
        font-family: "{font_family}", Consolas, monospace;
        font-size: {font_size}px;
        line-height: 1.35;
    }}
    QPlainTextEdit#CodeEditor {{
        background: {editor_bg};
    }}
    QPlainTextEdit#TerminalOutput, QLineEdit#TerminalInput {{
        background: {terminal_bg};
        font-family: "{font_family}", Consolas, monospace;
        font-size: {font_size}px;
    }}
    QListWidget, QTreeView {{
        background: {panel};
        border: none;
        outline: 0;
    }}
    QListWidget::item, QTreeView::item {{
        min-height: 25px;
        padding: 4px 7px;
    }}
    QListWidget::item:selected, QTreeView::item:selected {{
        background: {accent};
        color: white;
    }}
    QTabWidget::pane {{ border: none; }}
    QTabBar::tab {{
        background: {tab};
        color: {text};
        padding: 8px 14px;
        border-right: 1px solid {bg};
    }}
    QTabBar::tab:selected {{
        background: {editor_bg};
        color: {text};
    }}
    QLabel[muted="true"] {{ color: {muted}; }}
    QStatusBar {{
        background: {accent};
        color: white;
    }}
    QSplitter::handle {{ background: {side}; }}
    """


class WorkspaceDatabase:
    def __init__(self, project_path):
        prism_dir = os.path.join(project_path, ".prism")
        os.makedirs(prism_dir, exist_ok=True)
        self.path = os.path.join(prism_dir, "workspace.db")
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'new',
                priority TEXT DEFAULT 'medium',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS code_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                line_start INTEGER NOT NULL,
                line_end INTEGER NOT NULL,
                selected_text TEXT DEFAULT '',
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remind_at TEXT NOT NULL,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                started_at TEXT NOT NULL,
                seconds INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        self.connection.commit()

    def rows(self, query, values=()):
        return self.connection.execute(query, values).fetchall()

    def one(self, query, values=()):
        return self.connection.execute(query, values).fetchone()

    def execute(self, query, values=()):
        cursor = self.connection.execute(query, values)
        self.connection.commit()
        return cursor


class PluginManager:
    def __init__(self, app):
        self.app = app
        self.plugins = []
        self.commands = []
        self.completion_providers = []
        os.makedirs(PLUGINS_DIR, exist_ok=True)

    def load_plugins(self):
        self.plugins.clear()
        self.commands.clear()
        self.completion_providers.clear()
        for name in sorted(os.listdir(PLUGINS_DIR)):
            folder = os.path.join(PLUGINS_DIR, name)
            manifest_path = os.path.join(folder, "plugin.json")
            module_path = os.path.join(folder, "plugin.py")
            if os.path.isdir(folder) and os.path.exists(manifest_path) and os.path.exists(module_path):
                self.load_plugin(folder, manifest_path, module_path)

    def load_plugin(self, folder, manifest_path, module_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as file:
                manifest = json.load(file)
            module_name = f"prism_plugin_{os.path.basename(folder)}"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "activate"):
                module.activate(self.app)
            self.plugins.append({"folder": folder, "manifest": manifest})
        except Exception as error:
            self.app.statusBar().showMessage(f"Plugin error: {os.path.basename(folder)} - {error}", 6000)

    def register_command(self, title, callback):
        self.commands.append((title, callback))

    def register_completion_provider(self, provider):
        self.completion_providers.append(provider)

    def get_completions(self, context):
        result = []
        for provider in self.completion_providers:
            try:
                result.extend(provider(context) or [])
            except Exception:
                continue
        return sorted(set(result))


class LanguageHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        def text_format(color, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Bold)
            if italic:
                fmt.setFontItalic(True)
            return fmt

        keyword_format = text_format("#569cd6", True)
        string_format = text_format("#ce9178")
        comment_format = text_format("#6a9955", italic=True)
        number_format = text_format("#b5cea8")
        function_format = text_format("#dcdcaa")

        keywords = [
            "and", "as", "assert", "async", "await", "break", "case", "catch",
            "class", "const", "continue", "def", "elif", "else", "except",
            "false", "finally", "for", "from", "function", "if", "import",
            "in", "is", "lambda", "let", "new", "none", "not", "or", "pass",
            "raise", "return", "true", "try", "var", "while", "with", "yield",
        ]
        for word in keywords:
            self.rules.append((QRegExp(r"\b" + word + r"\b", Qt.CaseInsensitive), keyword_format))

        self.rules.extend(
            [
                (QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
                (QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format),
                (QRegExp(r"\b[0-9]+(\.[0-9]+)?\b"), number_format),
                (QRegExp(r"#.*"), comment_format),
                (QRegExp(r"//.*"), comment_format),
                (QRegExp(r"\b(def|function|class)\s+([A-Za-z_][A-Za-z0-9_]*)"), function_format),
            ]
        )

    def highlightBlock(self, text):
        for expression, fmt in self.rules:
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)


class EditorTab(QPlainTextEdit):
    def __init__(self, workspace, file_path=None, content=""):
        super().__init__()
        self.setObjectName("CodeEditor")
        self.workspace = workspace
        self.file_path = file_path
        self.setPlainText(content)
        self.highlighter = LanguageHighlighter(self.document())
        self.apply_editor_settings()

    def apply_editor_settings(self):
        family = self.workspace.settings.get("font_family", "Consolas")
        size = int(self.workspace.settings.get("font_size", 14))
        self.setFont(QFont(family, size))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.select(cursor.WordUnderCursor)
            word = cursor.selectedText()
            snippet = self.workspace.find_snippet(word)
            if snippet:
                cursor.insertText(snippet)
                return
        super().keyPressEvent(event)


class DevWorkspace(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.project_path = None
        self.db = None
        self.timer_started_at = None
        self.elapsed_seconds = 0
        self.run_process = None
        self.terminal_process = None
        self.snippets = {}

        self.plugin_manager = PluginManager(self)

        self.setWindowTitle("Prism Workspace")
        self.resize(1360, 800)
        self.init_ui()
        self.bind_shortcuts()
        self.apply_user_settings()

        self.plugin_manager.load_plugins()
        self.reload_plugins_panel()

        last_project = self.settings.get("last_project")
        if last_project and os.path.isdir(last_project):
            self.open_project(last_project)

        self.clock = QTimer(self)
        self.clock.timeout.connect(self.tick_timer)
        self.clock.start(1000)

        self.reminder_clock = QTimer(self)
        self.reminder_clock.timeout.connect(self.check_reminders)
        self.reminder_clock.start(30000)

    def init_ui(self):
        self.activity_bar = QWidget(objectName="ActivityBar")
        activity_layout = QVBoxLayout(self.activity_bar)
        activity_layout.setContentsMargins(6, 8, 6, 8)
        activity_layout.setSpacing(6)
        self.activity_bar.setFixedWidth(60)

        self.explorer_btn = self.side_button("Files")
        self.tasks_btn = self.side_button("Tasks")
        self.notes_btn = self.side_button("Notes")
        self.time_btn = self.side_button("Time")
        self.plugins_btn = self.side_button("Plug")
        for button in [self.explorer_btn, self.tasks_btn, self.notes_btn, self.time_btn, self.plugins_btn]:
            activity_layout.addWidget(button)
        activity_layout.addStretch()

        self.side_stack = QStackedWidget(objectName="SidePanel")
        self.side_stack.addWidget(self.build_explorer_panel())
        self.side_stack.addWidget(self.build_tasks_panel())
        self.side_stack.addWidget(self.build_notes_panel())
        self.side_stack.addWidget(self.build_time_panel())
        self.side_stack.addWidget(self.build_plugins_panel())

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_current_file_status)

        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setObjectName("TerminalOutput")
        self.terminal_output.setReadOnly(True)
        self.terminal_input = QLineEdit()
        self.terminal_input.setObjectName("TerminalInput")
        self.terminal_input.setPlaceholderText("Type a terminal command and press Enter")
        self.terminal_input.returnPressed.connect(self.send_terminal_input)

        terminal_panel = QWidget()
        terminal_layout = QVBoxLayout(terminal_panel)
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(4)
        terminal_header = QWidget()
        terminal_header_layout = QHBoxLayout(terminal_header)
        terminal_header_layout.setContentsMargins(8, 6, 8, 0)
        terminal_title = QLabel("TERMINAL")
        terminal_title.setProperty("muted", True)
        terminal_title.setStyleSheet("font-size: 11px; font-weight: 600;")
        self.terminal_start_btn = QPushButton("Start")
        self.terminal_start_btn.clicked.connect(self.start_terminal)
        self.terminal_stop_btn = QPushButton("Stop")
        self.terminal_stop_btn.clicked.connect(self.stop_terminal)
        terminal_header_layout.addWidget(terminal_title)
        terminal_header_layout.addStretch()
        terminal_header_layout.addWidget(self.terminal_start_btn)
        terminal_header_layout.addWidget(self.terminal_stop_btn)
        terminal_layout.addWidget(terminal_header)
        terminal_layout.addWidget(self.terminal_output)
        terminal_layout.addWidget(self.terminal_input)

        self.editor_splitter = QSplitter(Qt.Vertical)
        self.editor_splitter.addWidget(self.tabs)
        self.editor_splitter.addWidget(terminal_panel)
        self.editor_splitter.setSizes([580, 180])

        self.editor_stack = QStackedWidget()
        self.editor_stack.setObjectName("EditorSurface")
        self.welcome = self.build_welcome_panel()
        self.editor_stack.addWidget(self.welcome)
        self.editor_stack.addWidget(self.editor_splitter)
        self.projects_page = self.build_projects_page()
        self.settings_page = self.build_settings_panel()
        self.editor_stack.addWidget(self.projects_page)
        self.editor_stack.addWidget(self.settings_page)

        self.top_bar = self.build_top_menu_bar()

        main_editor = QWidget(objectName="MainEditor")
        main_editor_layout = QVBoxLayout(main_editor)
        main_editor_layout.setContentsMargins(0, 0, 0, 0)
        main_editor_layout.setSpacing(0)
        main_editor_layout.addWidget(self.top_bar)
        main_editor_layout.addWidget(self.editor_stack)

        left = QWidget()
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(self.activity_bar)
        left_layout.addWidget(self.side_stack)

        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(main_editor)
        splitter.setSizes([360, 1000])
        self.setCentralWidget(splitter)

        self.explorer_btn.clicked.connect(lambda: self.show_side_page(0))
        self.tasks_btn.clicked.connect(lambda: self.show_side_page(1))
        self.notes_btn.clicked.connect(lambda: self.show_side_page(2))
        self.time_btn.clicked.connect(lambda: self.show_side_page(3))
        self.plugins_btn.clicked.connect(lambda: self.show_side_page(4))
        self.show_side_page(0)
        self.show_editor_page()

        self.statusBar().showMessage("Ready")

    def bind_shortcuts(self):
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_current_file)
        self.addAction(save_action)

        open_action = QAction("Open Folder", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.choose_project_folder)
        self.addAction(open_action)

        run_action = QAction("Run", self)
        run_action.setShortcut("Ctrl+R")
        run_action.triggered.connect(self.run_current_file)
        self.addAction(run_action)

        complete_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        complete_shortcut.activated.connect(self.complete_current_word)

    def side_button(self, text):
        button = QPushButton(text)
        button.setObjectName("ActivityButton")
        button.setCheckable(True)
        button.setFixedSize(48, 40)
        return button

    def build_top_menu_bar(self):
        bar = QWidget(objectName="TopBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(6, 3, 8, 3)
        layout.setSpacing(2)
        bar.setFixedHeight(34)

        logo = QLabel("Prism")
        logo.setObjectName("WindowChromeLabel")
        layout.addWidget(logo)

        self.file_menu = QMenu(self)
        self.file_menu.addAction("New Project", self.create_project_folder)
        self.file_menu.addAction("Open Folder...", self.choose_project_folder)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Save", self.save_current_file)
        self.file_menu.addAction("Projects", self.show_projects_page)

        self.projects_menu = QMenu(self)
        self.projects_menu.addAction("Open Project Page", self.show_projects_page)
        self.projects_menu.addAction("Open Folder...", self.choose_project_folder)
        self.projects_menu.addAction("Create New Project", self.create_project_folder)

        self.edit_menu = QMenu(self)
        self.edit_menu.addAction("Complete Word", self.complete_current_word)
        self.edit_menu.addAction("Add Note To Selected Code", self.create_code_note_from_selection)

        self.selection_menu = QMenu(self)
        self.selection_menu.addAction("Attach Current File To Task", self.attach_current_file_to_task)

        self.view_menu = QMenu(self)
        self.view_menu.addAction("Editor", self.show_editor_page)
        self.view_menu.addAction("Projects", self.show_projects_page)
        self.view_menu.addAction("Settings", self.show_settings_page)
        self.view_menu.addSeparator()
        self.view_menu.addAction("Files Panel", lambda: self.show_side_page(0))
        self.view_menu.addAction("Tasks Panel", lambda: self.show_side_page(1))
        self.view_menu.addAction("Notes Panel", lambda: self.show_side_page(2))
        self.view_menu.addAction("Time Panel", lambda: self.show_side_page(3))
        self.view_menu.addAction("Plugins Panel", lambda: self.show_side_page(4))

        self.go_menu = QMenu(self)
        self.go_menu.addAction("Command Search", lambda: self.command_search.setFocus())
        self.go_menu.addAction("Settings", self.show_settings_page)
        self.plugin_commands_menu = self.go_menu.addMenu("Plugin Commands")

        self.run_menu = QMenu(self)
        self.run_menu.addAction("Run Python File", self.run_current_file)
        self.run_menu.addAction("Check Python Syntax", self.check_current_file)

        self.terminal_menu = QMenu(self)
        self.terminal_menu.addAction("Start Terminal", self.start_terminal)
        self.terminal_menu.addAction("Stop Terminal", self.stop_terminal)

        self.help_menu = QMenu(self)
        self.help_menu.addAction("Plugin Guide", self.show_plugin_guide_hint)
        self.help_menu.addAction("Reload Plugins", self.reload_plugins)

        for title, menu in [
            ("File", self.file_menu),
            ("Projects", self.projects_menu),
            ("Edit", self.edit_menu),
            ("Selection", self.selection_menu),
            ("View", self.view_menu),
            ("Go", self.go_menu),
            ("Run", self.run_menu),
            ("Terminal", self.terminal_menu),
            ("Help", self.help_menu),
        ]:
            button = self.menu_button(title, menu)
            layout.addWidget(button)

        layout.addStretch()
        self.command_search = QLineEdit()
        self.command_search.setObjectName("CommandSearch")
        self.command_search.setPlaceholderText("Search")
        self.command_search.setMaximumWidth(520)
        self.command_search.returnPressed.connect(self.run_command_search)
        layout.addWidget(self.command_search, 1)
        layout.addStretch()

        self.window_action_label = QLabel("split  layout  panel")
        self.window_action_label.setProperty("muted", True)
        self.window_action_label.setStyleSheet("font-size: 11px; padding: 0 8px;")
        layout.addWidget(self.window_action_label)
        return bar

    def menu_button(self, text, menu):
        button = QPushButton(text)
        button.setObjectName("MenuButton")
        button.setMenu(menu)
        return button

    def section_title(self, text):
        label = QLabel(text.upper())
        label.setProperty("muted", True)
        label.setStyleSheet("font-size: 11px; font-weight: 600; padding: 10px 8px 6px;")
        return label

    def show_editor_page(self):
        if self.project_path or self.tabs.count() > 0:
            self.editor_stack.setCurrentWidget(self.editor_splitter)
        else:
            self.editor_stack.setCurrentWidget(self.welcome)
        self.update_top_nav("editor")

    def show_projects_page(self):
        self.reload_recent_projects()
        self.editor_stack.setCurrentWidget(self.projects_page)
        self.update_top_nav("projects")

    def show_settings_page(self):
        self.editor_stack.setCurrentWidget(self.settings_page)
        self.update_top_nav("settings")

    def update_top_nav(self, active):
        self.active_top_page = active

    def run_command_search(self):
        query = self.command_search.text().strip().lower()
        self.command_search.clear()
        if not query:
            return

        commands = {
            "editor": self.show_editor_page,
            "projects": self.show_projects_page,
            "project": self.show_projects_page,
            "settings": self.show_settings_page,
            "preferences": self.show_settings_page,
            "run": self.run_current_file,
            "check": self.check_current_file,
            "terminal": self.start_terminal,
            "files": lambda: self.show_side_page(0),
            "tasks": lambda: self.show_side_page(1),
            "notes": lambda: self.show_side_page(2),
            "time": lambda: self.show_side_page(3),
            "plugins": lambda: self.show_side_page(4),
        }
        if query in commands:
            commands[query]()
            return

        for title, callback in self.plugin_manager.commands:
            if query in title.lower():
                callback()
                return
        self.statusBar().showMessage(f"No command found: {query}", 2500)

    def show_plugin_guide_hint(self):
        path = os.path.join(APP_DIR, "PLUGINS.md")
        if os.path.exists(path):
            self.open_file(path)
        else:
            QMessageBox.information(self, "Plugins", "Plugin documentation is stored in PLUGINS.md.")

    def build_welcome_panel(self):
        panel = QWidget()
        panel.setObjectName("WorkspacePage")
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        title = QLabel("Prism Workspace")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: 700;")
        subtitle = QLabel("Open a folder, keep code, tasks, notes and launches in one local workspace.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("muted", True)

        self.recent_projects = QListWidget()
        self.recent_projects.setFixedSize(520, 170)
        self.recent_projects.itemDoubleClicked.connect(lambda item: self.open_project(item.data(Qt.UserRole)))
        self.reload_recent_projects()

        open_button = QPushButton("Open project folder")
        open_button.setObjectName("PrimaryButton")
        open_button.setFixedWidth(220)
        open_button.clicked.connect(self.choose_project_folder)
        new_button = QPushButton("Create empty project")
        new_button.setFixedWidth(220)
        new_button.clicked.connect(self.create_project_folder)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(open_button)
        row.addWidget(new_button)
        row.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(row)
        layout.addWidget(self.section_title("Recent projects"), alignment=Qt.AlignCenter)
        layout.addWidget(self.recent_projects, alignment=Qt.AlignCenter)
        return panel

    def build_projects_page(self):
        panel = QWidget()
        panel.setObjectName("WorkspacePage")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        title = QLabel("Projects")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Open or create a local project without leaving the editor.")
        subtitle.setProperty("muted", True)

        self.projects_page_list = QListWidget()
        self.projects_page_list.itemDoubleClicked.connect(lambda item: self.open_project(item.data(Qt.UserRole)))

        open_button = QPushButton("Open Folder")
        open_button.setObjectName("PrimaryButton")
        open_button.clicked.connect(self.choose_project_folder)
        new_button = QPushButton("New Project")
        new_button.clicked.connect(self.create_project_folder)
        remove_button = QPushButton("Remove From Recent")
        remove_button.clicked.connect(self.remove_selected_recent_project)

        buttons = QHBoxLayout()
        buttons.addWidget(open_button)
        buttons.addWidget(new_button)
        buttons.addWidget(remove_button)
        buttons.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(buttons)
        layout.addWidget(self.section_title("Recent projects"))
        layout.addWidget(self.projects_page_list, 1)
        return panel

    def build_explorer_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 6)
        self.project_label = QLabel("No project")
        self.project_label.setStyleSheet("font-weight: 600;")
        header_layout.addWidget(self.project_label)
        header_layout.addStretch()

        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(False)
        self.tree.doubleClicked.connect(self.open_file_from_tree)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)

        layout.addWidget(header)
        layout.addWidget(self.section_title("Explorer"))
        layout.addWidget(self.tree)
        return panel

    def build_tasks_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.task_list = QListWidget()
        self.task_list.currentItemChanged.connect(self.load_selected_task)
        self.task_title = QLineEdit()
        self.task_title.setPlaceholderText("Task title")
        self.task_description = QPlainTextEdit()
        self.task_description.setPlaceholderText("What should be changed and where?")
        self.task_description.setMaximumHeight(110)
        self.task_status = QComboBox()
        self.task_status.addItems(["new", "in_progress", "done"])
        self.task_priority = QComboBox()
        self.task_priority.addItems(["low", "medium", "high"])

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_task)
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_task)
        attach_btn = QPushButton("Attach current file")
        attach_btn.clicked.connect(self.attach_current_file_to_task)

        self.related_files = QListWidget()
        self.related_files.itemDoubleClicked.connect(self.open_related_file)

        buttons = QHBoxLayout()
        buttons.addWidget(new_btn)
        buttons.addWidget(save_btn)
        form = QFormLayout()
        form.addRow("Status", self.task_status)
        form.addRow("Priority", self.task_priority)

        layout.addWidget(self.section_title("Tasks"))
        layout.addWidget(self.task_list, 2)
        layout.addWidget(self.task_title)
        layout.addWidget(self.task_description)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(attach_btn)
        layout.addWidget(self.section_title("Linked files"))
        layout.addWidget(self.related_files, 1)
        return panel

    def build_notes_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.notes_list = QListWidget()
        self.notes_list.currentItemChanged.connect(self.load_selected_note)
        self.note_title = QLineEdit()
        self.note_title.setPlaceholderText("Note title")
        self.note_body = QPlainTextEdit()
        self.note_body.setPlaceholderText("Quick project notes")

        new_note_btn = QPushButton("New")
        new_note_btn.clicked.connect(self.new_note)
        save_note_btn = QPushButton("Save")
        save_note_btn.clicked.connect(self.save_note)

        row = QHBoxLayout()
        row.addWidget(new_note_btn)
        row.addWidget(save_note_btn)

        layout.addWidget(self.section_title("Notes"))
        layout.addWidget(self.notes_list, 1)
        layout.addWidget(self.note_title)
        layout.addWidget(self.note_body, 2)
        layout.addLayout(row)
        return panel

    def build_time_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 30px; font-weight: 700;")
        start_btn = QPushButton("Start / Pause")
        start_btn.clicked.connect(self.toggle_timer)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_timer)

        self.reminder_text = QLineEdit()
        self.reminder_text.setPlaceholderText("Reminder text")
        self.reminder_time = QDateTimeEdit(QDateTime.currentDateTime().addSecs(900))
        self.reminder_time.setCalendarPopup(True)
        add_reminder_btn = QPushButton("Add reminder")
        add_reminder_btn.clicked.connect(self.add_reminder)
        self.reminder_list = QListWidget()

        layout.addWidget(self.section_title("Timer"))
        layout.addWidget(self.timer_label)
        layout.addWidget(start_btn)
        layout.addWidget(reset_btn)
        layout.addWidget(self.section_title("Reminders"))
        layout.addWidget(self.reminder_text)
        layout.addWidget(self.reminder_time)
        layout.addWidget(add_reminder_btn)
        layout.addWidget(self.reminder_list, 1)
        layout.addStretch()
        return panel

    def build_plugins_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.plugins_list = QListWidget()
        reload_btn = QPushButton("Reload plugins")
        reload_btn.clicked.connect(self.reload_plugins)
        open_folder_btn = QPushButton("Open plugins folder")
        open_folder_btn.clicked.connect(lambda: os.startfile(PLUGINS_DIR))

        self.plugin_hint = QLabel("Plugins live in the plugins folder. Each plugin has plugin.json and plugin.py.")
        self.plugin_hint.setWordWrap(True)
        self.plugin_hint.setProperty("muted", True)

        layout.addWidget(self.section_title("Plugins"))
        layout.addWidget(self.plugins_list)
        layout.addWidget(reload_btn)
        layout.addWidget(open_folder_btn)
        layout.addWidget(self.plugin_hint)
        layout.addStretch()
        return panel

    def build_settings_panel(self):
        panel = QWidget()
        panel.setObjectName("WorkspacePage")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Interface, editor font, colors and background image.")
        subtitle.setProperty("muted", True)

        self.language_combo = QComboBox()
        self.language_combo.addItem("Русский", "ru")
        self.language_combo.addItem("English", "en")
        self.language_combo.setCurrentIndex(0 if self.settings.get("language", "ru") == "ru" else 1)
        self.language_combo.currentIndexChanged.connect(lambda: self.update_language_setting(self.language_combo.currentData()))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "dark"))
        self.theme_combo.currentTextChanged.connect(self.update_theme_setting)

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.settings.get("font_family", "Consolas")))
        self.font_combo.currentFontChanged.connect(lambda font: self.update_font_setting(font.family()))

        self.font_size = QSpinBox()
        self.font_size.setRange(10, 28)
        self.font_size.setValue(int(self.settings.get("font_size", 14)))
        self.font_size.valueChanged.connect(self.update_font_size_setting)

        self.color_inputs = {}
        self.color_previews = {}

        def color_row(label, key):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            input_widget = QLineEdit(self.settings.get(key, DEFAULT_SETTINGS.get(key, "#000000")))
            preview = QLabel()
            preview.setFixedSize(48, 30)
            pick_button = QPushButton("Pick")
            pick_button.clicked.connect(lambda checked=False, k=key, field=input_widget: self.choose_color_for_setting(k, field))
            input_widget.textChanged.connect(lambda value, k=key: self.update_color_setting(k, value))
            self.color_inputs[key] = input_widget
            self.color_previews[key] = preview
            row_layout.addWidget(input_widget)
            row_layout.addWidget(preview)
            row_layout.addWidget(pick_button)
            return label, row

        self.background_image_input = QLineEdit(self.settings.get("background_image", ""))
        self.background_image_input.setPlaceholderText("Optional image path")
        self.background_image_input.textChanged.connect(self.update_background_image_setting)
        image_browse_btn = QPushButton("Browse")
        image_browse_btn.clicked.connect(self.choose_background_image)
        image_clear_btn = QPushButton("Clear")
        image_clear_btn.clicked.connect(self.clear_background_image)
        image_row = QWidget()
        image_row_layout = QHBoxLayout(image_row)
        image_row_layout.setContentsMargins(0, 0, 0, 0)
        image_row_layout.addWidget(self.background_image_input)
        image_row_layout.addWidget(image_browse_btn)
        image_row_layout.addWidget(image_clear_btn)

        self.settings_preview = QLabel("Live preview")
        self.settings_preview.setFixedHeight(44)

        form = QFormLayout()
        form.addRow("Language", self.language_combo)
        form.addRow("Theme", self.theme_combo)
        form.addRow("Editor font", self.font_combo)
        form.addRow("Font size", self.font_size)
        for label, row in [
            color_row("Accent", "accent_color"),
            color_row("App background", "background_color"),
            color_row("Side panel", "side_color"),
            color_row("Panel background", "panel_color"),
            color_row("Editor background", "editor_color"),
            color_row("Terminal background", "terminal_color"),
            color_row("Text", "text_color"),
        ]:
            form.addRow(label, row)
        form.addRow("Background image", image_row)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(self.settings_preview)
        layout.addStretch()
        self.update_appearance_preview()
        return panel

    def show_side_page(self, index):
        self.side_stack.setCurrentIndex(index)
        buttons = [self.explorer_btn, self.tasks_btn, self.notes_btn, self.time_btn, self.plugins_btn]
        for number, button in enumerate(buttons):
            button.setChecked(number == index)
            button.setProperty("active", number == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def apply_user_settings(self):
        self.setStyleSheet(build_style(self.settings))
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
            if isinstance(editor, EditorTab):
                editor.apply_editor_settings()
        self.update_appearance_preview()
        self.update_interface_language()

    def update_language_setting(self, value):
        self.settings["language"] = value
        save_settings(self.settings)
        self.update_interface_language()
        self.statusBar().showMessage("Language saved", 2000)

    def ui_text(self, key):
        texts = {
            "ru": {
                "editor": "Редактор",
                "projects": "Проекты",
                "settings": "Настройки",
                "open": "Открыть папку",
                "new": "Новый проект",
                "check": "Проверить",
                "run": "Запуск",
                "files": "Файлы",
                "tasks": "Задачи",
                "notes": "Заметки",
                "time": "Время",
                "plugins": "Плаг.",
                "terminal_start": "Старт",
                "terminal_stop": "Стоп",
                "terminal_input": "Введите команду терминала и нажмите Enter",
            },
            "en": {
                "editor": "Editor",
                "projects": "Projects",
                "settings": "Settings",
                "open": "Open Folder",
                "new": "New Project",
                "check": "Check",
                "run": "Run",
                "files": "Files",
                "tasks": "Tasks",
                "notes": "Notes",
                "time": "Time",
                "plugins": "Plug",
                "terminal_start": "Start",
                "terminal_stop": "Stop",
                "terminal_input": "Type a terminal command and press Enter",
            },
        }
        language = self.settings.get("language", "ru")
        return texts.get(language, texts["ru"]).get(key, key)

    def update_interface_language(self):
        if not hasattr(self, "terminal_start_btn"):
            return
        self.explorer_btn.setText(self.ui_text("files"))
        self.tasks_btn.setText(self.ui_text("tasks"))
        self.notes_btn.setText(self.ui_text("notes"))
        self.time_btn.setText(self.ui_text("time"))
        self.plugins_btn.setText(self.ui_text("plugins"))
        self.terminal_start_btn.setText(self.ui_text("terminal_start"))
        self.terminal_stop_btn.setText(self.ui_text("terminal_stop"))
        self.terminal_input.setPlaceholderText(self.ui_text("terminal_input"))

    def update_theme_setting(self, value):
        self.settings["theme"] = value
        save_settings(self.settings)
        self.apply_user_settings()

    def update_font_setting(self, family):
        self.settings["font_family"] = family
        save_settings(self.settings)
        self.apply_user_settings()

    def update_font_size_setting(self, size):
        self.settings["font_size"] = int(size)
        save_settings(self.settings)
        self.apply_user_settings()

    def update_color_setting(self, key, value):
        if QColor(value).isValid():
            self.settings[key] = QColor(value).name()
            save_settings(self.settings)
            self.apply_user_settings()

    def choose_color_for_setting(self, key, input_widget):
        color = QColorDialog.getColor(QColor(self.settings.get(key, DEFAULT_SETTINGS.get(key, "#000000"))), self, "Choose color")
        if color.isValid():
            input_widget.setText(color.name())

    def update_background_image_setting(self, value):
        self.settings["background_image"] = value.strip()
        save_settings(self.settings)
        self.apply_user_settings()

    def choose_background_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose background image",
            os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*.*)",
        )
        if path:
            self.background_image_input.setText(path)

    def clear_background_image(self):
        self.background_image_input.clear()

    def update_appearance_preview(self):
        if hasattr(self, "color_previews"):
            for key, preview in self.color_previews.items():
                color = setting_color(self.settings, key, DEFAULT_SETTINGS.get(key, "#000000"))
                preview.setStyleSheet(f"background: {color}; border: 1px solid #777; border-radius: 4px;")
                if key in self.color_inputs and self.color_inputs[key].text() != color:
                    self.color_inputs[key].blockSignals(True)
                    self.color_inputs[key].setText(color)
                    self.color_inputs[key].blockSignals(False)
        if hasattr(self, "settings_preview"):
            bg = setting_color(self.settings, "background_color", "#1e1f22")
            text = setting_color(self.settings, "text_color", "#d6d6d6")
            accent = setting_color(self.settings, "accent_color", "#0e639c")
            self.settings_preview.setText("Preview: buttons, editor and terminal update immediately")
            self.settings_preview.setStyleSheet(
                f"background: {bg}; color: {text}; border-left: 6px solid {accent}; "
                "border-radius: 6px; padding: 10px;"
            )

    def reload_recent_projects(self):
        lists = []
        if hasattr(self, "recent_projects"):
            lists.append(self.recent_projects)
        if hasattr(self, "projects_page_list"):
            lists.append(self.projects_page_list)
        for widget in lists:
            widget.clear()
        for path in self.settings.get("recent_projects", []):
            if os.path.isdir(path):
                for widget in lists:
                    item = QListWidgetItem(f"{os.path.basename(path)}\n{path}")
                    item.setData(Qt.UserRole, path)
                    widget.addItem(item)

    def remove_selected_recent_project(self):
        item = self.projects_page_list.currentItem() if hasattr(self, "projects_page_list") else None
        if not item:
            return
        path = item.data(Qt.UserRole)
        self.settings["recent_projects"] = [p for p in self.settings.get("recent_projects", []) if p != path]
        if self.settings.get("last_project") == path:
            self.settings["last_project"] = ""
        save_settings(self.settings)
        self.reload_recent_projects()

    def choose_project_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open project folder", self.project_path or os.path.expanduser("~"))
        if folder:
            self.open_project(folder)

    def create_project_folder(self):
        base = QFileDialog.getExistingDirectory(self, "Select parent folder", os.path.expanduser("~"))
        if not base:
            return
        name, ok = QInputDialog.getText(self, "New project", "Project folder name:")
        if not ok or not name.strip():
            return
        path = os.path.join(base, name.strip())
        os.makedirs(path, exist_ok=True)
        main_file = os.path.join(path, "main.py")
        if not os.path.exists(main_file):
            with open(main_file, "w", encoding="utf-8") as file:
                file.write('print("Hello from Prism Workspace")\n')
        self.open_project(path)

    def open_project(self, folder):
        self.project_path = os.path.abspath(folder)
        if self.db:
            self.db.connection.close()
        self.db = WorkspaceDatabase(self.project_path)

        recent = [p for p in self.settings.get("recent_projects", []) if p != self.project_path]
        recent.insert(0, self.project_path)
        self.settings["recent_projects"] = recent[:8]
        self.settings["last_project"] = self.project_path
        save_settings(self.settings)
        self.reload_recent_projects()

        self.file_model.setRootPath(self.project_path)
        self.tree.setRootIndex(self.file_model.index(self.project_path))
        self.project_label.setText(os.path.basename(self.project_path) or self.project_path)
        self.setWindowTitle(f"{os.path.basename(self.project_path)} - Prism Workspace")
        self.statusBar().showMessage(self.project_path)
        self.editor_stack.setCurrentWidget(self.editor_splitter)
        self.update_top_nav("editor")

        self.reload_tasks()
        self.reload_notes()
        self.reload_reminders()
        if self.terminal_process and self.terminal_process.state() != QProcess.NotRunning:
            self.terminal_process.write(f'cd "{self.project_path}"\n'.encode("utf-8"))

    def require_project(self):
        if self.db:
            return True
        QMessageBox.information(self, "Project required", "Open a project folder first.")
        return False

    def open_file_from_tree(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.open_file(file_path)

    def open_file(self, file_path):
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
            if editor and editor.file_path == file_path:
                self.tabs.setCurrentIndex(index)
                return

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
        except OSError as error:
            QMessageBox.warning(self, "Cannot open file", str(error))
            return

        editor = EditorTab(self, file_path, content)
        editor.textChanged.connect(self.mark_current_tab_dirty)
        index = self.tabs.addTab(editor, os.path.basename(file_path))
        self.tabs.setCurrentIndex(index)
        self.editor_stack.setCurrentWidget(self.editor_splitter)

    def close_tab(self, index):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0 and not self.project_path:
            self.editor_stack.setCurrentWidget(self.welcome)

    def current_editor(self):
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, EditorTab) else None

    def current_file_path(self):
        editor = self.current_editor()
        return editor.file_path if editor else None

    def save_current_file(self):
        editor = self.current_editor()
        if not editor or not editor.file_path:
            return
        try:
            with open(editor.file_path, "w", encoding="utf-8") as file:
                file.write(editor.toPlainText())
        except OSError as error:
            QMessageBox.warning(self, "Cannot save file", str(error))
            return
        self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(editor.file_path))
        self.statusBar().showMessage("File saved", 2000)

    def mark_current_tab_dirty(self):
        index = self.tabs.currentIndex()
        if index >= 0:
            title = self.tabs.tabText(index)
            if not title.startswith("*"):
                self.tabs.setTabText(index, "*" + title)

    def update_current_file_status(self):
        path = self.current_file_path()
        if path:
            self.statusBar().showMessage(path)

    def complete_current_word(self):
        editor = self.current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.select(cursor.WordUnderCursor)
        prefix = cursor.selectedText()
        words = self.plugin_manager.get_completions(self.completion_context(prefix))
        match = next((word for word in words if word.startswith(prefix) and word != prefix), None)
        if match:
            cursor.insertText(match)
            self.statusBar().showMessage(f"Completed: {match}", 1500)

    def find_snippet(self, word):
        return self.snippets.get(word)

    def register_snippet(self, trigger, body):
        self.snippets[trigger] = body

    def completion_context(self, prefix=""):
        editor = self.current_editor()
        file_path = self.current_file_path()
        return {
            "prefix": prefix,
            "file_path": file_path,
            "extension": os.path.splitext(file_path or "")[1],
            "text": editor.toPlainText() if editor else "",
        }

    def insert_text(self, text):
        editor = self.current_editor()
        if editor:
            editor.textCursor().insertText(text)

    def get_selected_code_info(self):
        editor = self.current_editor()
        file_path = self.current_file_path()
        if not editor or not file_path:
            return None
        cursor = editor.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n")
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        text_before_start = editor.toPlainText()[:start]
        text_before_end = editor.toPlainText()[:end]
        return {
            "file_path": file_path,
            "relative_path": os.path.relpath(file_path, self.project_path) if self.project_path else file_path,
            "line_start": text_before_start.count("\n") + 1,
            "line_end": text_before_end.count("\n") + 1,
            "selected_text": selected,
        }

    def create_code_note_from_selection(self):
        if not self.require_project():
            return
        info = self.get_selected_code_info()
        if not info:
            QMessageBox.information(self, "Code note", "Open a file and select code first.")
            return
        body, ok = QInputDialog.getMultiLineText(self, "Code note", "Note for selected code:")
        if not ok or not body.strip():
            return
        self.db.execute(
            """
            INSERT INTO code_notes(file_path, line_start, line_end, selected_text, body, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                info["relative_path"],
                info["line_start"],
                info["line_end"],
                info["selected_text"],
                body.strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self.statusBar().showMessage("Code note saved", 2000)

    def reload_plugins(self):
        self.plugin_manager.load_plugins()
        self.reload_plugins_panel()
        self.statusBar().showMessage("Plugins reloaded", 2000)

    def reload_plugins_panel(self):
        if hasattr(self, "plugins_list"):
            self.plugins_list.clear()
            for plugin in self.plugin_manager.plugins:
                manifest = plugin["manifest"]
                self.plugins_list.addItem(f"{manifest.get('name', 'Plugin')}  v{manifest.get('version', '0.1')}")
        if hasattr(self, "plugin_commands_menu"):
            self.plugin_commands_menu.clear()
            if not self.plugin_manager.commands:
                empty_action = self.plugin_commands_menu.addAction("No plugin commands")
                empty_action.setEnabled(False)
            for title, callback in self.plugin_manager.commands:
                self.plugin_commands_menu.addAction(title, callback)

    def run_plugin_command_from_combo(self, index):
        if index <= 0 or not hasattr(self, "command_combo"):
            return
        callback = self.command_combo.itemData(index)
        self.command_combo.setCurrentIndex(0)
        if callback:
            callback()

    def run_current_file(self):
        path = self.current_file_path()
        if not path:
            QMessageBox.information(self, "Run", "Open a file first.")
            return
        self.save_current_file()
        if self.run_process and self.run_process.state() != QProcess.NotRunning:
            self.run_process.kill()

        ext = os.path.splitext(path)[1].lower()
        if ext == ".py":
            program = sys.executable
            args = [path]
        else:
            QMessageBox.information(self, "Run", "The MVP runner supports Python files now.")
            return

        self.terminal_output.clear()
        self.terminal_output.appendPlainText(f"> {program} {path}\n")
        self.run_process = QProcess(self)
        self.run_process.setWorkingDirectory(self.project_path or os.path.dirname(path))
        self.run_process.readyReadStandardOutput.connect(self.read_run_output)
        self.run_process.readyReadStandardError.connect(self.read_run_error)
        self.run_process.finished.connect(lambda code, status: self.terminal_output.appendPlainText(f"\nProcess finished with code {code}"))
        self.run_process.start(program, args)
        self.editor_splitter.setSizes([520, 240])

    def check_current_file(self):
        path = self.current_file_path()
        if not path:
            QMessageBox.information(self, "Check", "Open a file first.")
            return
        self.save_current_file()
        ext = os.path.splitext(path)[1].lower()
        if ext != ".py":
            QMessageBox.information(self, "Check", "The MVP compiler check supports Python files now.")
            return
        if self.run_process and self.run_process.state() != QProcess.NotRunning:
            self.run_process.kill()
        self.terminal_output.clear()
        self.terminal_output.appendPlainText(f"> {sys.executable} -m py_compile {path}\n")
        self.run_process = QProcess(self)
        self.run_process.setWorkingDirectory(self.project_path or os.path.dirname(path))
        self.run_process.readyReadStandardOutput.connect(self.read_run_output)
        self.run_process.readyReadStandardError.connect(self.read_run_error)
        self.run_process.finished.connect(self.on_check_finished)
        self.run_process.start(sys.executable, ["-m", "py_compile", path])
        self.editor_splitter.setSizes([520, 240])

    def on_check_finished(self, code, status):
        if code == 0:
            self.terminal_output.appendPlainText("\nCheck passed: no Python syntax errors.")
        else:
            self.terminal_output.appendPlainText(f"\nCheck failed with code {code}.")

    def read_run_output(self):
        self.terminal_output.appendPlainText(bytes(self.run_process.readAllStandardOutput()).decode("utf-8", errors="ignore"))

    def read_run_error(self):
        self.terminal_output.appendPlainText(bytes(self.run_process.readAllStandardError()).decode("utf-8", errors="ignore"))

    def terminal_program(self):
        if os.name == "nt":
            return "powershell.exe", ["-NoLogo", "-NoExit", "-ExecutionPolicy", "Bypass"]
        return os.environ.get("SHELL", "/bin/sh"), []

    def start_terminal(self):
        if self.terminal_process and self.terminal_process.state() != QProcess.NotRunning:
            return
        program, args = self.terminal_program()
        self.terminal_process = QProcess(self)
        self.terminal_process.setWorkingDirectory(self.project_path or os.path.expanduser("~"))
        self.terminal_process.readyReadStandardOutput.connect(self.read_terminal_output)
        self.terminal_process.readyReadStandardError.connect(self.read_terminal_error)
        self.terminal_process.finished.connect(lambda code, status: self.terminal_output.appendPlainText(f"\nTerminal stopped with code {code}"))
        self.terminal_output.appendPlainText(f"> Starting terminal: {program}\n")
        self.terminal_process.start(program, args)

    def stop_terminal(self):
        if self.terminal_process and self.terminal_process.state() != QProcess.NotRunning:
            self.terminal_process.kill()

    def read_terminal_output(self):
        self.terminal_output.appendPlainText(bytes(self.terminal_process.readAllStandardOutput()).decode("utf-8", errors="ignore"))

    def read_terminal_error(self):
        self.terminal_output.appendPlainText(bytes(self.terminal_process.readAllStandardError()).decode("utf-8", errors="ignore"))

    def send_terminal_input(self):
        command = self.terminal_input.text()
        if not command.strip():
            return
        if not self.terminal_process or self.terminal_process.state() == QProcess.NotRunning:
            self.start_terminal()
        if self.terminal_process and self.terminal_process.state() != QProcess.NotRunning:
            self.terminal_output.appendPlainText(f"\n> {command}")
            self.terminal_process.write((command + "\n").encode("utf-8"))
        self.terminal_input.clear()

    def reload_tasks(self):
        self.task_list.clear()
        if not self.db:
            return
        rows = self.db.rows("SELECT * FROM tasks ORDER BY id DESC")
        for row in rows:
            item = QListWidgetItem(f"[{row['status']}] {row['title']}")
            item.setData(Qt.UserRole, row["id"])
            self.task_list.addItem(item)
        self.new_task(clear_only=True)

    def new_task(self, clear_only=False):
        self.task_list.setCurrentItem(None)
        self.task_title.clear()
        self.task_description.clear()
        self.task_status.setCurrentText("new")
        self.task_priority.setCurrentText("medium")
        self.related_files.clear()
        if not clear_only:
            self.task_title.setFocus()

    def load_selected_task(self, current, previous=None):
        if not current or not self.db:
            return
        task_id = current.data(Qt.UserRole)
        row = self.db.one("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not row:
            return
        self.task_title.setText(row["title"])
        self.task_description.setPlainText(row["description"])
        self.task_status.setCurrentText(row["status"])
        self.task_priority.setCurrentText(row["priority"])
        self.reload_related_files(task_id)

    def selected_task_id(self):
        item = self.task_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def save_task(self):
        if not self.require_project():
            return
        title = self.task_title.text().strip()
        if not title:
            return
        task_id = self.selected_task_id()
        values = (
            title,
            self.task_description.toPlainText().strip(),
            self.task_status.currentText(),
            self.task_priority.currentText(),
        )
        if task_id:
            self.db.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ?, priority = ? WHERE id = ?",
                values + (task_id,),
            )
        else:
            self.db.execute(
                "INSERT INTO tasks(title, description, status, priority, created_at) VALUES (?, ?, ?, ?, ?)",
                values + (datetime.now().isoformat(timespec="seconds"),),
            )
        self.reload_tasks()

    def attach_current_file_to_task(self):
        if not self.require_project():
            return
        task_id = self.selected_task_id()
        file_path = self.current_file_path()
        if not task_id or not file_path:
            QMessageBox.information(self, "Link file", "Select a task and open a file first.")
            return
        relative = os.path.relpath(file_path, self.project_path)
        exists = self.db.one("SELECT id FROM task_files WHERE task_id = ? AND file_path = ?", (task_id, relative))
        if not exists:
            self.db.execute("INSERT INTO task_files(task_id, file_path) VALUES (?, ?)", (task_id, relative))
        self.reload_related_files(task_id)

    def reload_related_files(self, task_id):
        self.related_files.clear()
        rows = self.db.rows("SELECT file_path FROM task_files WHERE task_id = ? ORDER BY file_path", (task_id,))
        for row in rows:
            self.related_files.addItem(row["file_path"])

    def open_related_file(self, item):
        if self.project_path:
            self.open_file(os.path.join(self.project_path, item.text()))

    def reload_notes(self):
        self.notes_list.clear()
        if not self.db:
            return
        rows = self.db.rows("SELECT * FROM notes ORDER BY updated_at DESC")
        for row in rows:
            item = QListWidgetItem(row["title"])
            item.setData(Qt.UserRole, row["id"])
            self.notes_list.addItem(item)
        self.new_note(clear_only=True)

    def new_note(self, clear_only=False):
        self.notes_list.setCurrentItem(None)
        self.note_title.clear()
        self.note_body.clear()
        if not clear_only:
            self.note_title.setFocus()

    def load_selected_note(self, current, previous=None):
        if not current or not self.db:
            return
        note_id = current.data(Qt.UserRole)
        row = self.db.one("SELECT * FROM notes WHERE id = ?", (note_id,))
        if row:
            self.note_title.setText(row["title"])
            self.note_body.setPlainText(row["body"])

    def save_note(self):
        if not self.require_project():
            return
        title = self.note_title.text().strip()
        if not title:
            return
        note_id = self.notes_list.currentItem().data(Qt.UserRole) if self.notes_list.currentItem() else None
        values = (title, self.note_body.toPlainText().strip(), datetime.now().isoformat(timespec="seconds"))
        if note_id:
            self.db.execute("UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?", values + (note_id,))
        else:
            self.db.execute("INSERT INTO notes(title, body, updated_at) VALUES (?, ?, ?)", values)
        self.reload_notes()

    def toggle_timer(self):
        if self.timer_started_at is None:
            self.timer_started_at = time.time()
        else:
            session_seconds = int(time.time() - self.timer_started_at)
            self.elapsed_seconds += session_seconds
            self.timer_started_at = None
            self.save_time_entry(session_seconds)
        self.update_timer_label()

    def reset_timer(self):
        self.timer_started_at = None
        self.elapsed_seconds = 0
        self.update_timer_label()

    def tick_timer(self):
        self.update_timer_label()

    def update_timer_label(self):
        seconds = self.elapsed_seconds
        if self.timer_started_at is not None:
            seconds += int(time.time() - self.timer_started_at)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        self.timer_label.setText(f"{hours:02}:{minutes:02}:{secs:02}")

    def save_time_entry(self, seconds):
        if not self.db or seconds <= 0:
            return
        self.db.execute(
            "INSERT INTO time_entries(task_id, started_at, seconds) VALUES (?, ?, ?)",
            (self.selected_task_id(), datetime.now().isoformat(timespec="seconds"), seconds),
        )

    def add_reminder(self):
        if not self.require_project():
            return
        text = self.reminder_text.text().strip()
        if not text:
            return
        remind_at = self.reminder_time.dateTime().toPyDateTime().isoformat(timespec="seconds")
        self.db.execute("INSERT INTO reminders(remind_at, text) VALUES (?, ?)", (remind_at, text))
        self.reminder_text.clear()
        self.reload_reminders()

    def reload_reminders(self):
        self.reminder_list.clear()
        if not self.db:
            return
        rows = self.db.rows("SELECT * FROM reminders WHERE done = 0 ORDER BY remind_at")
        for row in rows:
            item = QListWidgetItem(f"{row['remind_at'].replace('T', ' ')}  {row['text']}")
            item.setData(Qt.UserRole, row["id"])
            self.reminder_list.addItem(item)

    def check_reminders(self):
        if not self.db:
            return
        now = datetime.now().isoformat(timespec="seconds")
        rows = self.db.rows("SELECT * FROM reminders WHERE done = 0 AND remind_at <= ?", (now,))
        for row in rows:
            QMessageBox.information(self, "Reminder", row["text"])
            self.db.execute("UPDATE reminders SET done = 1 WHERE id = ?", (row["id"],))
        if rows:
            self.reload_reminders()

    def closeEvent(self, event):
        if self.run_process and self.run_process.state() != QProcess.NotRunning:
            self.run_process.kill()
        if self.terminal_process and self.terminal_process.state() != QProcess.NotRunning:
            self.terminal_process.kill()
        if self.db:
            self.db.connection.close()
        super().closeEvent(event)
