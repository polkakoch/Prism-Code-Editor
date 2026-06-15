def activate(app):
    app.plugin_manager.register_command("Add note to selected code", app.create_code_note_from_selection)
