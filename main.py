import sys, os, json
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QHBoxLayout
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
    return {"language": "ru"}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

settings = load_settings()
lang = settings.get("language", "ru")

LANG = {
    "ru": {
        "title": "Prism Code Editor",
        "add_project": "Добавить проект",
        "choose_folder": "Выберите папку проекта",
        "app_name": "PrismCE",
        "language": "Русский",
    },
    "en": {
        "title": "Prism Code Editor",
        "add_project": "Add project",
        "choose_folder": "Select project folder",
        "app_name": "PrismCE",
        "language": "English",
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
        projects.append({"name": project_name, "path": folder})
        project_list.addItem(project_name)
        save_projects(projects)

open_editors = []

def on_project_selected():
    selected_item = project_list.currentItem()
    if selected_item:
        name = selected_item.text()
        project = next((p for p in projects if p["name"] == name), None)
        if project:
            editor_window = CodeEditor(project["path"])
            editor_window.show()
            open_editors.append(editor_window)

def switch_language():
    global lang
    lang = "en" if lang == "ru" else "ru"
    settings["language"] = lang
    save_settings(settings)
    update_language()

def update_language():
    window.setWindowTitle(LANG[lang]["title"])
    name.setText(LANG[lang]["app_name"])
    open_folder.setText(LANG[lang]["add_project"])
    lang_button.setText("🇷🇺" if lang == "en" else "🇬🇧")


app = QApplication([])

window = QWidget()
window.resize(900, 540)
window.setWindowTitle(LANG[lang]["title"])

main_layout = QVBoxLayout()
top_layout = QHBoxLayout()

name = QLabel(LANG[lang]["app_name"])
name.setFont(QFont("Arial", 20))
name.setAlignment(Qt.AlignLeft | Qt.AlignTop)

lang_button = QPushButton("🇬🇧" if lang == "ru" else "🇷🇺")
lang_button.setFixedSize(50, 30)
lang_button.clicked.connect(switch_language)

top_layout.addWidget(name)
top_layout.addStretch()
top_layout.addWidget(lang_button)

open_folder = QPushButton(LANG[lang]["add_project"])
open_folder.setFixedSize(200, 36)
open_folder.clicked.connect(open_folder_click)

project_list = QListWidget()
project_list.itemDoubleClicked.connect(on_project_selected)

projects = load_projects()
for p in projects:
    project_list.addItem(p["name"])

main_layout.addLayout(top_layout)
main_layout.addWidget(project_list)
main_layout.addWidget(open_folder, alignment=Qt.AlignBottom)

window.setLayout(main_layout)
apply_stylesheet(app, theme='dark_purple.xml')

window.show()
sys.exit(app.exec_())
