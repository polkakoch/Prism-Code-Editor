import ast
import builtins
import keyword
import re


def completion(label, insert_text=None, kind="word", detail="", documentation="", priority=100, filter_text=None):
    return {
        "label": label,
        "insert_text": insert_text or label,
        "filter_text": filter_text or label.rstrip("()"),
        "kind": kind,
        "detail": detail,
        "documentation": documentation,
        "priority": priority,
    }


SNIPPETS = {
    "main": 'if __name__ == "__main__":\n    main()\n',
    "defn": "def function_name():\n    pass\n",
    "classn": "class ClassName:\n    def __init__(self):\n        pass\n",
    "trye": "try:\n    pass\nexcept Exception as error:\n    print(error)\n",
    "fori": "for index in range(10):\n    print(index)\n",
    "whilet": "while True:\n    pass\n",
    "withopen": 'with open("file.txt", "r", encoding="utf-8") as file:\n    content = file.read()\n',
    "dataclass": "@dataclass\nclass ClassName:\n    value: str\n",
}


SNIPPET_COMPLETIONS = [
    completion(trigger, body, "snippet", "Python code template", priority=5, filter_text=trigger)
    for trigger, body in SNIPPETS.items()
]


KEYWORD_COMPLETIONS = [
    completion(word, kind="keyword", detail="Python keyword", priority=40)
    for word in sorted(keyword.kwlist)
]


BUILTIN_COMPLETIONS = [
    completion(f"{name}()", f"{name}($0)", "function", "built-in", priority=50, filter_text=name)
    for name in sorted(dir(builtins))
    if not name.startswith("_") and callable(getattr(builtins, name))
] + [
    completion(name, kind="constant", detail="built-in", priority=55)
    for name in ["False", "None", "True", "Ellipsis", "NotImplemented"]
]


COMMON_MODULES = [
    "argparse", "asyncio", "collections", "csv", "dataclasses", "datetime", "functools",
    "itertools", "json", "logging", "math", "os", "pathlib", "random", "re", "sqlite3",
    "subprocess", "sys", "time", "typing", "unittest", "urllib",
]


MODULE_COMPLETIONS = [
    completion(name, kind="module", detail="standard library", priority=70)
    for name in COMMON_MODULES
]


DOT_COMPLETIONS = {
    "os": [
        completion("getcwd()", "getcwd()", "function", "os", priority=10),
        completion("listdir()", "listdir($0)", "function", "os", priority=10),
        completion("makedirs()", "makedirs($0, exist_ok=True)", "function", "os", priority=10),
        completion("path.join()", "path.join($0)", "function", "os.path", priority=10, filter_text="path.join"),
        completion("path.exists()", "path.exists($0)", "function", "os.path", priority=10, filter_text="path.exists"),
        completion("path.basename()", "path.basename($0)", "function", "os.path", priority=10, filter_text="path.basename"),
    ],
    "os.path": [
        completion("join()", "join($0)", "function", "os.path", priority=10),
        completion("exists()", "exists($0)", "function", "os.path", priority=10),
        completion("basename()", "basename($0)", "function", "os.path", priority=10),
        completion("dirname()", "dirname($0)", "function", "os.path", priority=10),
        completion("abspath()", "abspath($0)", "function", "os.path", priority=10),
    ],
    "sys": [
        completion("argv", kind="attribute", detail="sys", priority=10),
        completion("executable", kind="attribute", detail="sys", priority=10),
        completion("exit()", "exit($0)", "function", "sys", priority=10),
        completion("path", kind="attribute", detail="sys", priority=10),
    ],
    "json": [
        completion("load()", "load($0)", "function", "json", priority=10),
        completion("loads()", "loads($0)", "function", "json", priority=10),
        completion("dump()", "dump($0)", "function", "json", priority=10),
        completion("dumps()", "dumps($0, ensure_ascii=False, indent=2)", "function", "json", priority=10),
    ],
    "datetime": [
        completion("datetime", kind="class", detail="datetime", priority=10),
        completion("date", kind="class", detail="datetime", priority=10),
        completion("timedelta", kind="class", detail="datetime", priority=10),
        completion("now()", "now()", "function", "datetime", priority=10),
    ],
    "math": [
        completion("sqrt()", "sqrt($0)", "function", "math", priority=10),
        completion("ceil()", "ceil($0)", "function", "math", priority=10),
        completion("floor()", "floor($0)", "function", "math", priority=10),
        completion("pi", kind="constant", detail="math", priority=10),
    ],
    "re": [
        completion("search()", "search($0)", "function", "re", priority=10),
        completion("match()", "match($0)", "function", "re", priority=10),
        completion("findall()", "findall($0)", "function", "re", priority=10),
        completion("sub()", "sub($0)", "function", "re", priority=10),
        completion("compile()", "compile($0)", "function", "re", priority=10),
    ],
    "pathlib": [
        completion("Path()", "Path($0)", "class", "pathlib", priority=10),
    ],
    "Path": [
        completion("exists()", "exists()", "method", "Path", priority=10),
        completion("read_text()", 'read_text(encoding="utf-8")', "method", "Path", priority=10),
        completion("write_text()", 'write_text($0, encoding="utf-8")', "method", "Path", priority=10),
        completion("iterdir()", "iterdir()", "method", "Path", priority=10),
        completion("mkdir()", "mkdir(parents=True, exist_ok=True)", "method", "Path", priority=10),
    ],
    "list": [
        completion("append()", "append($0)", "method", "list", priority=10),
        completion("extend()", "extend($0)", "method", "list", priority=10),
        completion("insert()", "insert($0)", "method", "list", priority=10),
        completion("pop()", "pop()", "method", "list", priority=10),
        completion("remove()", "remove($0)", "method", "list", priority=10),
        completion("sort()", "sort()", "method", "list", priority=10),
    ],
    "dict": [
        completion("get()", "get($0)", "method", "dict", priority=10),
        completion("items()", "items()", "method", "dict", priority=10),
        completion("keys()", "keys()", "method", "dict", priority=10),
        completion("values()", "values()", "method", "dict", priority=10),
        completion("update()", "update($0)", "method", "dict", priority=10),
        completion("setdefault()", "setdefault($0)", "method", "dict", priority=10),
    ],
    "str": [
        completion("strip()", "strip()", "method", "str", priority=10),
        completion("lower()", "lower()", "method", "str", priority=10),
        completion("upper()", "upper()", "method", "str", priority=10),
        completion("replace()", "replace($0)", "method", "str", priority=10),
        completion("split()", "split($0)", "method", "str", priority=10),
        completion("startswith()", "startswith($0)", "method", "str", priority=10),
        completion("endswith()", "endswith($0)", "method", "str", priority=10),
        completion("format()", "format($0)", "method", "str", priority=10),
    ],
    "file": [
        completion("read()", "read()", "method", "file", priority=10),
        completion("readline()", "readline()", "method", "file", priority=10),
        completion("readlines()", "readlines()", "method", "file", priority=10),
        completion("write()", "write($0)", "method", "file", priority=10),
        completion("close()", "close()", "method", "file", priority=10),
    ],
}


def completion_provider(context):
    if context.get("extension") != ".py":
        return []

    text = context.get("text", "")
    before_cursor = context.get("before_cursor", "")
    current_line = context.get("current_line", "")

    dot_target = dotted_target(before_cursor)
    if dot_target:
        return completions_for_dot_target(dot_target, text, before_cursor)

    if looks_like_import_line(current_line):
        return MODULE_COMPLETIONS

    return (
        SNIPPET_COMPLETIONS
        + local_symbol_completions(text)
        + KEYWORD_COMPLETIONS
        + BUILTIN_COMPLETIONS
        + MODULE_COMPLETIONS
    )


def dotted_target(before_cursor):
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\.([A-Za-z_][A-Za-z0-9_]*)?$", before_cursor)
    if not match:
        return ""
    target = match.group(1)
    return target if target in DOT_COMPLETIONS else target.split(".")[-1]


def looks_like_import_line(line):
    stripped = line.strip()
    return stripped.startswith("import ") or stripped.startswith("from ")


def completions_for_dot_target(target, text, before_cursor):
    aliases = imported_aliases(text)
    canonical = aliases.get(target, target)
    if canonical in DOT_COMPLETIONS:
        return DOT_COMPLETIONS[canonical]

    inferred = infer_simple_type(target, before_cursor)
    if inferred in DOT_COMPLETIONS:
        return DOT_COMPLETIONS[inferred]
    return []


def imported_aliases(text):
    aliases = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return aliases

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = item.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for item in node.names:
                aliases[item.asname or item.name] = item.name if module in ("pathlib", "datetime") else module
    return aliases


def infer_simple_type(name, before_cursor):
    lower = name.lower()
    if lower in {"text", "line", "name", "message", "content", "prefix", "suffix", "path"}:
        return "str"
    if lower in {"items", "rows", "lines", "files", "plugins", "values", "results"}:
        return "list"
    if lower in {"data", "settings", "config", "context", "manifest", "payload", "headers"}:
        return "dict"
    if lower in {"file", "source", "output", "stream"}:
        return "file"

    assignment_patterns = [
        (rf"\b{name}\s*=\s*\[", "list"),
        (rf"\b{name}\s*=\s*list\(", "list"),
        (rf"\b{name}\s*=\s*\{{", "dict"),
        (rf"\b{name}\s*=\s*dict\(", "dict"),
        (rf"\b{name}\s*=\s*['\"]", "str"),
        (rf"\b{name}\s*=\s*str\(", "str"),
        (rf"\b{name}\s*=\s*Path\(", "Path"),
        (rf"\b{name}\s*=\s*open\(", "file"),
    ]
    for pattern, inferred in assignment_patterns:
        if re.search(pattern, before_cursor):
            return inferred
    return ""


def local_symbol_completions(text):
    items = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return regex_symbol_fallback(text)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ", ".join(arg.arg for arg in node.args.args if arg.arg != "self")
            insert_args = "$0" if not args else args
            items.append(
                completion(
                    f"{node.name}()",
                    f"{node.name}({insert_args})",
                    "function",
                    f"line {node.lineno}",
                    priority=20,
                    filter_text=node.name,
                )
            )
        elif isinstance(node, ast.ClassDef):
            items.append(completion(node.name, kind="class", detail=f"line {node.lineno}", priority=20))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for name in target_names(target):
                    items.append(completion(name, kind="variable", detail=f"line {node.lineno}", priority=30))
        elif isinstance(node, ast.For):
            for name in target_names(node.target):
                items.append(completion(name, kind="variable", detail=f"line {node.lineno}", priority=30))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias, module in imported_aliases_from_node(node):
                items.append(completion(alias, kind="module", detail=module, priority=25))
    return items


def regex_symbol_fallback(text):
    items = []
    for match in re.finditer(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.MULTILINE):
        name = match.group(1)
        items.append(completion(f"{name}()", f"{name}($0)", "function", "current file", priority=25, filter_text=name))
    for match in re.finditer(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.MULTILINE):
        items.append(completion(match.group(1), kind="class", detail="current file", priority=25))
    return items


def target_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names = []
        for child in target.elts:
            names.extend(target_names(child))
        return names
    return []


def imported_aliases_from_node(node):
    if isinstance(node, ast.Import):
        return [(item.asname or item.name.split(".")[0], item.name) for item in node.names]
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        return [(item.asname or item.name, module) for item in node.names]
    return []


def insert_main_block(app):
    app.insert_text(SNIPPETS["main"])


def insert_dataclass_template(app):
    app.insert_text("from dataclasses import dataclass\n\n" + SNIPPETS["dataclass"])


def activate(app):
    app.plugin_manager.register_completion_provider(completion_provider)
    app.plugin_manager.register_command("Python: insert main block", lambda: insert_main_block(app))
    app.plugin_manager.register_command("Python: insert dataclass template", lambda: insert_dataclass_template(app))
    for trigger, body in SNIPPETS.items():
        app.register_snippet(trigger, body)
