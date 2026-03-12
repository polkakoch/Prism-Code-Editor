import sys, os, json
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QHBoxLayout, QMenu, QInputDialog,
    QDialog, QLineEdit, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet
from editor import CodeEditor

PROJECTS_FILE = "projects.json"
SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Значения по умолчанию: русский язык и тёмная синяя тема
    return {"language": "ru", "theme": "dark_blue.xml"}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

settings = load_settings()
if "theme" not in settings:
    settings["theme"] = "dark_blue.xml"
lang = settings.get("language", "ru")

LANG = {
    "ru": {
        "title": "Prism Code Editor",
        "project_button": "Создать проект",
        "add_project": "Открыть существующий проект",
        "new_project": "Создать новый проект",
        "choose_folder": "Выберите папку проекта",
        "app_name": "PrismCE",
        "language": "Русский",
        "rename_project": "Переименовать проект",
        "delete_project": "Удалить проект",
        "pin_project": "Закрепить",
        "unpin_project": "Открепить",
        "new_project_name": "Введите имя нового проекта:",
        "rename_project_name": "Новое имя проекта:",
        "select_base_folder": "Выберите папку, где создать проект",
        "select_project_type": "Выберите тип проекта:",
        "type_python": "Python",
        "type_js": "JavaScript",
        "type_django": "Django",
        "settings": "Настройки",
        "ui_language": "Язык интерфейса",
        "theme": "Тема",
    },
    "en": {
        "title": "Prism Code Editor",
        "project_button": "Create project",
        "add_project": "Open existing project",
        "new_project": "Create new project",
        "choose_folder": "Select project folder",
        "app_name": "PrismCE",
        "language": "English",
        "rename_project": "Rename project",
        "delete_project": "Delete project",
        "pin_project": "Pin",
        "unpin_project": "Unpin",
        "new_project_name": "Enter new project name:",
        "rename_project_name": "New project name:",
        "select_base_folder": "Select base folder for project",
        "select_project_type": "Select project type:",
        "type_python": "Python",
        "type_js": "JavaScript",
        "type_django": "Django",
        "settings": "Settings",
        "ui_language": "Interface language",
        "theme": "Theme",
    }
}


def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


def open_folder_click():
    folder = QFileDialog.getExistingDirectory(None, LANG[lang]["choose_folder"], "C:\\")
    if folder:
        project_name = os.path.basename(folder)
        # По умолчанию считаем Python-проектом
        projects.append({
            "name": project_name,
            "path": folder,
            "pinned": False,
            "type": "python"
        })
        refresh_project_list()
        save_projects(projects)


def create_new_project():
    # Окно создания нового проекта (имя + язык + расположение)
    dialog = QDialog()
    dialog.setWindowTitle(LANG[lang]["new_project"])
    dialog.setModal(True)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: Segoe UI, Arial;
        }
        QLineEdit, QComboBox {
            background-color: #3c3f41;
            border: 1px solid #555555;
            padding: 4px 6px;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #3c7dd9;
            color: white;
            border-radius: 4px;
            padding: 4px 12px;
        }
        QPushButton:hover {
            background-color: #4c8df0;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #aaaaaa;
        }
    """)

    vbox = QVBoxLayout(dialog)
    vbox.setSpacing(8)

    name_label = QLabel(LANG[lang]["new_project_name"])
    name_edit = QLineEdit()

    type_label = QLabel(LANG[lang]["select_project_type"])
    type_combo = QComboBox()
    type_combo.addItem(LANG[lang]["type_python"], "python")
    type_combo.addItem(LANG[lang]["type_js"], "javascript")
    type_combo.addItem(LANG[lang]["type_django"], "django")

    location_label = QLabel(LANG[lang]["select_base_folder"])
    location_button = QPushButton("Выбрать..." if lang == "ru" else "Browse...")
    location_display = QLabel("C:\\" if lang == "ru" else "C:\\")

    def choose_location():
        base = QFileDialog.getExistingDirectory(dialog, LANG[lang]["select_base_folder"], "C:\\")
        if base:
            location_display.setText(base)
    location_button.clicked.connect(choose_location)

    buttons_row = QHBoxLayout()
    create_btn = QPushButton(LANG[lang]["new_project"])
    cancel_btn = QPushButton("Отмена" if lang == "ru" else "Cancel")

    def on_create():
        if not name_edit.text().strip():
            return
        dialog.accept()

    def on_cancel():
        dialog.reject()

    create_btn.clicked.connect(on_create)
    cancel_btn.clicked.connect(on_cancel)

    buttons_row.addStretch()
    buttons_row.addWidget(create_btn)
    buttons_row.addWidget(cancel_btn)

    vbox.addWidget(name_label)
    vbox.addWidget(name_edit)
    vbox.addWidget(type_label)
    vbox.addWidget(type_combo)

    loc_row = QHBoxLayout()
    loc_row.addWidget(location_label)
    loc_row.addStretch()
    loc_row.addWidget(location_button)
    vbox.addLayout(loc_row)
    vbox.addWidget(location_display)

    vbox.addLayout(buttons_row)

    if dialog.exec_() != QDialog.Accepted:
        return

    name = name_edit.text().strip()
    if not name:
        return
    base_folder = location_display.text().strip() or "C:\\"
    project_type = type_combo.currentData() or "python"

    new_path = os.path.join(base_folder, name)
    try:
        os.makedirs(new_path, exist_ok=True)
    except OSError:
        return

    # Лёгкий скелет проекта под язык
    if project_type in ("python", "django"):
        main_file = os.path.join(new_path, "main.py")
        if not os.path.exists(main_file):
            with open(main_file, "w", encoding="utf-8") as f:
                f.write("# " + name + " — Python project\n")
    elif project_type == "javascript":
        main_file = os.path.join(new_path, "index.js")
        if not os.path.exists(main_file):
            with open(main_file, "w", encoding="utf-8") as f:
                f.write("// " + name + " — JavaScript project\n")

    projects.append({
        "name": name,
        "path": new_path,
        "pinned": False,
        "type": project_type
    })
    refresh_project_list()
    save_projects(projects)

open_editors = []

def on_project_selected():
    selected_item = project_list.currentItem()
    if selected_item:
        # Текст в списке может содержать иконку, поэтому ищем по имени в словаре данных
        item_text = selected_item.text()
        project = next((p for p in projects if format_project_label(p) == item_text), None)
        if project:
            editor_window = CodeEditor(project["path"], project.get("type", "python"))
            editor_window.show()
            open_editors.append(editor_window)
            window.close()


def project_context_menu(pos):
    item = project_list.itemAt(pos)
    if item is None:
        return

    name = item.text()
    project = next((p for p in projects if p["name"] == name), None)
    if not project:
        return

    menu = QMenu()
    rename_action = menu.addAction(LANG[lang]["rename_project"])
    delete_action = menu.addAction(LANG[lang]["delete_project"])
    pin_text = LANG[lang]["unpin_project"] if project.get("pinned") else LANG[lang]["pin_project"]
    pin_action = menu.addAction(pin_text)

    action = menu.exec_(project_list.mapToGlobal(pos))
    if action is None:
        return

    if action == rename_action:
        new_name, ok = QInputDialog.getText(
            window,
            LANG[lang]["rename_project"],
            LANG[lang]["rename_project_name"],
            text=project["name"]
        )
        if ok and new_name:
            project["name"] = new_name
            refresh_project_list()
            save_projects(projects)

    elif action == delete_action:
        projects.remove(project)
        refresh_project_list()
        save_projects(projects)

    elif action == pin_action:
        project["pinned"] = not project.get("pinned", False)
        refresh_project_list()
        save_projects(projects)


def refresh_project_list():
    project_list.clear()
    # Сначала закреплённые, потом остальные
    sorted_projects = sorted(
        projects,
        key=lambda p: (not p.get("pinned", False), p["name"].lower())
    )
    for p in sorted_projects:
        project_list.addItem(format_project_label(p))


def format_project_label(project):
    icon = "🐍"
    if project.get("type") == "javascript":
        icon = "🟨"
    elif project.get("type") == "django":
        icon = "🌿"
    name = project.get("name", "")
    return f"{icon}  {name}"

def switch_language():
    global lang
    lang = "en" if lang == "ru" else "ru"
    settings["language"] = lang
    save_settings(settings)
    update_language()


def open_settings_dialog():
    global lang, settings
    dialog = QDialog(window)
    dialog.setWindowTitle(LANG[lang]["settings"])
    dialog.setModal(True)

    layout = QVBoxLayout(dialog)
    layout.setSpacing(10)

    # Выбор языка интерфейса
    lang_label = QLabel(LANG[lang]["ui_language"])
    lang_combo = QComboBox()
    lang_combo.addItem("Русский", "ru")
    lang_combo.addItem("English", "en")
    current_lang_index = 0 if lang == "ru" else 1
    lang_combo.setCurrentIndex(current_lang_index)

    # Выбор темы (тёмные/светлые варианты: розовый, красный, фиолетовый, зелёный, синий)
    theme_label = QLabel(LANG[lang]["theme"])
    theme_combo = QComboBox()
    if lang == "ru":
        theme_options = [
            ("Тёмная — Синяя", "dark_blue.xml"),
            ("Тёмная — Розовая", "dark_pink.xml"),
            ("Тёмная — Красная", "dark_red.xml"),
            ("Тёмная — Фиолетовая", "dark_purple.xml"),
            ("Тёмная — Зелёная", "dark_green.xml"),
            ("Светлая — Синяя", "light_blue.xml"),
            ("Светлая — Розовая", "light_pink.xml"),
            ("Светлая — Красная", "light_red.xml"),
            ("Светлая — Фиолетовая", "light_purple.xml"),
            ("Светлая — Зелёная", "light_green.xml"),
        ]
    else:
        theme_options = [
            ("Dark — Blue", "dark_blue.xml"),
            ("Dark — Pink", "dark_pink.xml"),
            ("Dark — Red", "dark_red.xml"),
            ("Dark — Purple", "dark_purple.xml"),
            ("Dark — Green", "dark_green.xml"),
            ("Light — Blue", "light_blue.xml"),
            ("Light — Pink", "light_pink.xml"),
            ("Light — Red", "light_red.xml"),
            ("Light — Purple", "light_purple.xml"),
            ("Light — Green", "light_green.xml"),
        ]
    for label_text, value in theme_options:
        theme_combo.addItem(label_text, value)

    theme_value = settings.get("theme", "dark_blue.xml")
    for i in range(theme_combo.count()):
        if theme_combo.itemData(i) == theme_value:
            theme_combo.setCurrentIndex(i)
            break

    buttons = QHBoxLayout()
    ok_btn = QPushButton("OK")
    cancel_btn = QPushButton("Отмена" if lang == "ru" else "Cancel")

    def on_ok():
        global lang
        lang = lang_combo.currentData()
        settings["language"] = lang
        settings["theme"] = theme_combo.currentData()
        save_settings(settings)
        apply_app_theme()
        update_language()
        dialog.accept()

    def on_cancel():
        dialog.reject()

    ok_btn.clicked.connect(on_ok)
    cancel_btn.clicked.connect(on_cancel)

    buttons.addStretch()
    buttons.addWidget(ok_btn)
    buttons.addWidget(cancel_btn)

    layout.addWidget(lang_label)
    layout.addWidget(lang_combo)
    layout.addWidget(theme_label)
    layout.addWidget(theme_combo)
    layout.addLayout(buttons)

    dialog.exec_()


def apply_app_theme():
    # Поддержка старых значений из настроек
    legacy_map = {
        "dark": "dark_blue.xml",
        "light": "light_blue.xml",
        "jetbrains": "dark_purple.xml",
    }
    theme_value = settings.get("theme", "dark_blue.xml")
    if theme_value in legacy_map:
        theme_value = legacy_map[theme_value]
        settings["theme"] = theme_value
        save_settings(settings)

    apply_stylesheet(app, theme=theme_value)

def update_language():
    window.setWindowTitle(LANG[lang]["title"])
    name.setText(LANG[lang]["app_name"])
    project_button.setText(LANG[lang]["project_button"])


app = QApplication([])

window = QWidget()
window.resize(900, 540)
window.setWindowTitle(LANG[lang]["title"])
window.setStyleSheet("""
    QWidget {
        background-color: #2b2b2b;
        color: #e0e0e0;
        font-family: Segoe UI, Arial;
        font-size: 13px;
    }
""")

main_layout = QVBoxLayout()
top_layout = QHBoxLayout()

name = QLabel(LANG[lang]["app_name"])
name.setFont(QFont("Segoe UI", 22, QFont.Bold))
name.setAlignment(Qt.AlignLeft | Qt.AlignTop)

settings_button = QPushButton("⚙")
settings_button.setFixedSize(56, 40)
settings_button.setStyleSheet("""
    QPushButton {
        font-size: 20px;
        background-color: transparent;
        border: none;
        color: #e0e0e0;
    }
    QPushButton:hover {
        color: #ffffff;
    }
""")
settings_button.clicked.connect(open_settings_dialog)

top_layout.addWidget(name)
top_layout.addStretch()
top_layout.addWidget(settings_button)

project_list = QListWidget()
project_list.itemDoubleClicked.connect(on_project_selected)
project_list.setContextMenuPolicy(Qt.CustomContextMenu)
project_list.customContextMenuRequested.connect(project_context_menu)
project_list.setStyleSheet("""
    QListWidget {
        background-color: #252526;
        border: 1px solid #2d2d2d;
        padding: 6px;
    }
    QListWidget::item {
        padding: 6px 10px;
    }
    QListWidget::item:selected {
        background-color: #094771;
    }
""")

projects = load_projects()
# Обновляем структуру (добавляем pinned / type, если их нет)
for p in projects:
    if "pinned" not in p:
        p["pinned"] = False
    if "type" not in p:
        p["type"] = "python"
refresh_project_list()

buttons_layout = QHBoxLayout()
project_button = QPushButton(LANG[lang]["project_button"])
project_button.setFixedHeight(44)
project_button.setStyleSheet("""
    QPushButton {
        background-color: #007ACC;
        color: white;
        border-radius: 6px;
        padding: 0 24px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0090ff;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
""")
def project_button_click():
    menu = QMenu()
    open_action = menu.addAction(LANG[lang]["add_project"])
    create_action = menu.addAction(LANG[lang]["new_project"])
    action = menu.exec_(project_button.mapToGlobal(project_button.rect().bottomLeft()))
    if action == open_action:
        open_folder_click()
    elif action == create_action:
        create_new_project()

project_button.clicked.connect(project_button_click)

buttons_layout.addStretch()
buttons_layout.addWidget(project_button)
buttons_layout.addStretch()

main_layout.addLayout(top_layout)
main_layout.addWidget(project_list)
main_layout.addLayout(buttons_layout)

window.setLayout(main_layout)
apply_app_theme()

window.show()
sys.exit(app.exec_())
