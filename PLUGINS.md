# Prism Workspace Plugin Guide

Plugins are local folders inside `plugins/`.

Each plugin has two required files:

```text
plugins/
  my_plugin/
    plugin.json
    plugin.py
```

## Manifest

`plugin.json` describes the extension:

```json
{
  "id": "my_plugin",
  "name": "My Plugin",
  "version": "0.1.0",
  "description": "What the plugin does.",
  "entry": "plugin.py"
}
```

Required fields:

- `id` - stable plugin identifier and folder name after ZIP install.
- `name` - readable plugin name.
- `version` - plugin version.
- `description` - short text shown in the plugin manager.
- `entry` - Python file with `activate(app)`, usually `plugin.py`.

## Python Entry Point

`plugin.py` must define `activate(app)`.

```python
def activate(app):
    app.plugin_manager.register_command("Say hello", lambda: app.statusBar().showMessage("Hello", 2000))
```

The `app` object is the main `DevWorkspace` window. For MVP plugins, use only these public methods:

- `app.plugin_manager.register_command(title, callback)` adds a command to the top command list.
- `app.plugin_manager.register_completion_provider(provider)` adds local autocomplete words.
- `app.register_snippet(trigger, body)` adds a snippet inserted with `Tab`.
- `app.insert_text(text)` inserts text into the current editor.
- `app.get_selected_code_info()` returns the current file, selected text and line range.
- `app.create_code_note_from_selection()` opens a note dialog and saves a note for selected code.
- `app.current_file_path()` returns the opened file path.
- `app.completion_context(prefix)` returns data for autocomplete.

## Completion Provider

A completion provider receives a context dictionary and returns a list of words.

```python
def completion_provider(context):
    if context["extension"] != ".py":
        return []
    return ["print", "range", "requests", "datetime"]


def activate(app):
    app.plugin_manager.register_completion_provider(completion_provider)
```

Completion providers may also return dictionaries for richer popup items:

```python
def completion_provider(context):
    return [
        {
            "label": "print()",
            "insert_text": "print($0)",
            "filter_text": "print",
            "kind": "function",
            "detail": "built-in",
            "documentation": "Writes values to stdout.",
            "priority": 20
        }
    ]
```

`$0` marks where the cursor should be placed after insertion. Press `Ctrl+Space` to open the completion popup, use arrows to choose an item, then press `Enter` or `Tab`.

## Snippets

Snippets are inserted when the user types the trigger and presses `Tab`.

```python
def activate(app):
    app.register_snippet("main", 'if __name__ == "__main__":\n    main()\n')
```

## Example Plugins

`plugins/python_assistant` adds context-aware Python completions, snippets, local file symbols and common dot-completions.

`plugins/code_notes` adds the command `Add note to selected code`. The note is saved in the project database table `code_notes`.

## Plugin Manager

Open the `Plug` side panel to manage installed plugins.

- `Install ZIP` installs a plugin archive into the local `plugins/` folder.
- `Enable plugin` / `Disable plugin` stores plugin state in `settings.json`.
- `Reload plugins` scans the folder again and shows validation or load errors.

The loader validates `plugin.json`, checks that the entry file stays inside the plugin folder and keeps broken plugins isolated from the main app.

## ZIP Distribution

A plugin can be distributed as a zip archive:

```text
python_assistant.zip
  python_assistant/
    plugin.json
    plugin.py
```

The user unpacks it into `plugins/`, then clicks `Reload plugins` in Prism Workspace.
