# Prism Workspace

Prism Workspace is a local desktop workspace for developers. It combines a code editor, project tree, tasks, notes, timer, reminders, terminal runner and a small plugin system.

The app is local-first: no internet connection and no neural networks are required.

## Run

```bash
pip install -r requirements.txt
python main.py
```

The editor opens immediately. A project can be selected inside the app with `Open Folder`, created with `New Project`, or opened from the recent projects list.

## Current MVP Features

- Minimal dark/light UI inspired by VS Code and Atom.
- VS Code-style top menu: `File`, `Projects`, `Edit`, `Selection`, `View`, `Go`, `Run`, `Terminal`, `Help`.
- Search/command field in the top bar.
- Built-in project picker and recent projects page inside the editor.
- Project file tree.
- File tabs.
- Edit and save files with `Ctrl+S`.
- Basic syntax highlighting.
- Tasks with status, priority and linked project files.
- Notes stored in the project database.
- Timer and reminders.
- Settings page with language, theme, editor font, font size, HTML colors and live previews.
- Background image selection in the same settings page.
- Python run button, separate Python syntax check button and terminal panel.
- Integrated shell terminal with direct typing in the terminal panel, command history and project working directory.
- Plugin manager with ZIP install, enable/disable state, validation and load errors.
- Context-aware Python Assistant plugin with completion popup, snippets, local symbols and common dot-completions.

## Project Structure

```text
Prism-Code-Editor-main/
  main.py
  editor.py
  requirements.txt
  settings.json
  PLUGINS.md
  plugins/
    python_assistant/
      plugin.json
      plugin.py
    code_notes/
      plugin.json
      plugin.py
```

For a larger version, split `editor.py` into modules:

```text
app/
  main.py
  core/
    database.py
    plugins.py
    settings.py
    project.py
  ui/
    main_window.py
    explorer_panel.py
    tasks_panel.py
    notes_panel.py
    settings_panel.py
    terminal_panel.py
  widgets/
    code_editor.py
    highlighter.py
```

## Database

Each project stores local data in:

```text
project/
  .prism/
    workspace.db
```

Main tables:

- `tasks` - task title, description, status, priority.
- `task_files` - links between tasks and project files.
- `notes` - project notes.
- `code_notes` - notes attached to a concrete file and line range.
- `reminders` - in-app reminders.
- `time_entries` - tracked work sessions.

## Plugins

Plugins are placed in the `plugins/` folder. Each plugin has:

```text
plugin.json
plugin.py
```

The app includes two example plugins:

- `python_assistant` - context-aware Python completions and snippets.
- `code_notes` - command for attaching a note to selected code.

Read [PLUGINS.md](PLUGINS.md) for the plugin API and examples.

## How To Use Python Assistant

Open a `.py` file.

- Press `Ctrl+Space` to open the completion popup.
- Use arrows to choose a completion, then press `Enter` or `Tab`.
- Type `main`, `defn`, `classn`, `trye` or `fori`, then press `Tab` to insert a snippet.
- The plugin also suggests local functions, classes, variables, imported modules and common Python methods after `.`.

## How To Use Code Notes

1. Open a project and a file.
2. Select a code fragment.
3. In the top command list choose `Add note to selected code`.
4. Enter the note text.

The note is saved in SQLite in the `code_notes` table with file path and line range.

## Terminal And Code Check

The bottom panel works like a simple VS Code-style terminal.

- `Start` opens a local shell process if it is not already running.
- Type commands directly in the terminal panel and press `Enter`.
- Use `Up` and `Down` to browse command history.
- `Run` saves and runs the current Python file.
- `Check` runs `python -m py_compile` for the current Python file and reports syntax errors.

The command terminal and the Python runner are separate processes, so normal commands and file execution do not block each other.

## Appearance Settings

Open the top `Settings` tab to change:

- interface language setting;
- theme;
- editor font;
- font size;
- accent color;
- app background color;
- side panel color;
- panel color;
- editor background color;
- terminal background color;
- text color;
- optional background image.

Colors can be entered as HTML values like `#0e639c` or selected with the color picker. Changes are applied immediately.

## Next Useful Steps

- Add terminal command history and tabs.
- Add a table view for code notes.
- Add search by file name and text.
- Split the current large `editor.py` into smaller modules.
