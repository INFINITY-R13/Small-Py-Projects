"""
Syntax rules and highlighting engine for Aura Text Editor.
Fast regex-based tokenizer supporting Python, Markdown, JSON, HTML, CSS, JS, Shell, and SQL.
"""

import bisect
import os
import re

EXT_MAP = {
    ".py": "python",
    ".pyw": "python",
    ".md": "markdown",
    ".markdown": "markdown",
    ".json": "json",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".html": "html",
    ".htm": "html",
    ".xml": "html",
    ".css": "css",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".sql": "sql",
    ".txt": "plaintext",
}

LANGUAGE_NAMES = {
    "python": "Python",
    "markdown": "Markdown",
    "json": "JSON",
    "javascript": "JavaScript",
    "html": "HTML",
    "css": "CSS",
    "bash": "Shell",
    "sql": "SQL",
    "plaintext": "Plain Text",
}

def detect_language(filepath: str) -> str:
    if not filepath:
        return "plaintext"
    ext = os.path.splitext(filepath)[1].lower()
    return EXT_MAP.get(ext, "plaintext")


# Syntax regex definitions
PYTHON_RULES = [
    # Multi-line strings
    ("string", r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'),
    # Single-line strings
    ("string", r'(?:"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'),
    # Comments
    ("comment", r'#.*$'),
    # Decorators
    ("decorator", r'@[A-Za-z_][A-Za-z0-9_.]*'),
    # Class definition name
    ("class", r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)'),
    # Function definition name
    ("function", r'\bdef\s+([A-Za-z_][A-Za-z0-9_]*)'),
    # Keywords
    (
        "keyword",
        r'\b(def|class|return|if|elif|else|while|for|in|try|except|finally|with|as|'
        r'lambda|yield|raise|async|await|pass|break|continue|import|from|global|nonlocal|'
        r'assert|is|not|and|or)\b',
    ),
    # Booleans and None
    ("boolean", r'\b(True|False|None)\b'),
    # Builtins
    (
        "builtin",
        r'\b(print|len|range|enumerate|zip|dict|list|set|tuple|str|int|float|bool|'
        r'super|type|isinstance|open|input|sum|min|max|any|all|abs|round|dir|id|help|'
        r'map|filter|iter|next|format|slice|sorted|reversed|hasattr|getattr|setattr|'
        r'delattr|property|classmethod|staticmethod|self|cls)\b',
    ),
    # Numbers
    ("number", r'\b0[xX][0-9a-fA-F]+\b|\b0[bB][01]+\b|\b0[oO][0-7]+\b|\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b'),
    # Operators
    ("operator", r'(\+|-|\*|/|//|%|\*\*|==|!=|<=|>=|<|>|=|&|\||\^|~|->)'),
]

MARKDOWN_RULES = [
    # Code blocks
    ("md_code", r'```[\s\S]*?```'),
    # Inline code
    ("md_code", r'`[^`]+`'),
    # Headers
    ("md_header", r'^#{1,6}\s+.*$'),
    # Bold
    ("md_bold", r'(\*\*[^*]+?\*\*|__[^_]+?__)'),
    # Italic
    ("md_italic", r'(\*[^*]+?\*|_[^_]+?_)'),
    # Links
    ("md_link", r'\[.*?\]\(.*?\)'),
    # Blockquotes
    ("comment", r'^>.*$'),
    # Lists
    ("operator", r'^[\s]*[-*+]\s+|^[\s]*\d+\.\s+'),
]

JSON_RULES = [
    # Keys
    ("json_key", r'"([^"\\]|\\.)*"\s*(?=:)'),
    # Strings (values)
    ("string", r'"([^"\\]|\\.)*"'),
    # Numbers
    ("number", r'\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b'),
    # Booleans and null
    ("boolean", r'\b(true|false|null)\b'),
    # Delimiters
    ("operator", r'[:,\{\}\[\]]'),
]

JAVASCRIPT_RULES = [
    # Strings
    ("string", r'(`[\s\S]*?`|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'),
    # Comments
    ("comment", r'(//.*$|/\*[\s\S]*?\*/)'),
    # Keywords
    (
        "keyword",
        r'\b(function|return|if|else|while|for|in|of|do|switch|case|default|break|continue|'
        r'var|let|const|class|extends|new|this|typeof|instanceof|void|delete|throw|try|'
        r'catch|finally|import|export|from|as|await|async|yield|debugger)\b',
    ),
    # Booleans and null/undefined
    ("boolean", r'\b(true|false|null|undefined|NaN|Infinity)\b'),
    # Functions
    ("function", r'\b([A-Za-z_$][A-Za-z0-9_$]*)\s*(?=\()'),
    # Builtins
    (
        "builtin",
        r'\b(console|window|document|Math|JSON|Promise|Array|Object|String|Number|'
        r'Boolean|RegExp|Date|Map|Set|Symbol|setTimeout|setInterval)\b',
    ),
    # Numbers
    ("number", r'\b\d+(?:\.\d+)?\b'),
    # Operators
    ("operator", r'(\+|-|\*|/|%|===|!==|==|!=|<=|>=|<|>|=|\&\&|\|\||!|\?|=>)'),
]

HTML_RULES = [
    # Comments
    ("comment", r'<!--[\s\S]*?-->'),
    # Tags
    ("keyword", r'</?[a-zA-Z0-9_-]+'),
    # Attribute values
    ("string", r'="[^"]*"|=\'[^\']*\''),
    # Attribute names
    ("function", r'\b[a-zA-Z0-9_-]+(?=\=)'),
    # Closing bracket
    ("operator", r'/?>'),
]

CSS_RULES = [
    # Comments
    ("comment", r'/\*[\s\S]*?\*/'),
    # Strings
    ("string", r'("[^"]*"|\'[^\']*\')'),
    # Properties
    ("keyword", r'\b[a-z-]+(?=\s*:)'),
    # Units and numbers
    ("number", r'\b\d+(?:\.\d+)?(px|rem|em|%|vh|vw|pt|s|ms|deg)?\b'),
    # Colors (#hex)
    ("class", r'#[0-9a-fA-F]{3,8}\b'),
    # Selectors / classes / ids
    ("function", r'[.#][a-zA-Z0-9_-]+'),
]

BASH_RULES = [
    # Comments
    ("comment", r'#.*$'),
    # Strings
    ("string", r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'),
    # Variables
    ("decorator", r'\$[A-Za-z_0-9]+|\$\{[A-Za-z_0-9]+\}'),
    # Keywords
    (
        "keyword",
        r'\b(if|then|else|elif|fi|case|esac|for|while|until|do|done|in|function|'
        r'return|exit|export|local|read|echo|printf|cd|pwd|source)\b',
    ),
    # Numbers
    ("number", r'\b\d+\b'),
    # Operators
    ("operator", r'(\||\&|;|>|<|>>|<<|&&|\|\|)'),
]

SQL_RULES = [
    # Comments
    ("comment", r'(--.*$|/\*[\s\S]*?\*/)'),
    # Strings
    ("string", r'(\'(?:\\.|[^\'\\])*\'|"(?:\\.|[^"\\])*")'),
    # Keywords
    (
        "keyword",
        r'\b(SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|'
        r'DROP|ALTER|ADD|COLUMN|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP|BY|ORDER|'
        r'HAVING|LIMIT|OFFSET|AS|AND|OR|NOT|IN|LIKE|IS|NULL|DISTINCT|UNION|ALL|'
        r'CASE|WHEN|THEN|ELSE|END|PRIMARY|KEY|FOREIGN|REFERENCES|INDEX)\b',
    ),
    # Builtin functions
    (
        "builtin",
        r'\b(COUNT|SUM|AVG|MIN|MAX|NOW|COALESCE|CONCAT|UPPER|LOWER|LENGTH|TRIM)\b',
    ),
    # Numbers
    ("number", r'\b\d+(?:\.\d+)?\b'),
]

RULES = {
    "python": PYTHON_RULES,
    "markdown": MARKDOWN_RULES,
    "json": JSON_RULES,
    "javascript": JAVASCRIPT_RULES,
    "html": HTML_RULES,
    "css": CSS_RULES,
    "bash": BASH_RULES,
    "sql": SQL_RULES,
    "plaintext": [],
}


class SyntaxHighlighter:
    """Fast regex syntax highlighter with line/col caching and region tagging."""

    def __init__(self, text_widget, language: str = "plaintext"):
        self.text_widget = text_widget
        self.language = language
        self._compiled_rules = {}
        self._compile_rules()

    def _compile_rules(self):
        rules = RULES.get(self.language, [])
        compiled = []
        flags = re.MULTILINE
        if self.language in ("sql",):
            flags |= re.IGNORECASE
        for tag, pattern in rules:
            try:
                compiled.append((tag, re.compile(pattern, flags)))
            except re.error:
                pass
        self._compiled_rules = compiled

    def set_language(self, language: str):
        if self.language != language:
            self.language = language
            self._compile_rules()
            self.highlight_all()

    def highlight_all(self):
        """Highlights the entire content of text_widget quickly."""
        if not self._compiled_rules:
            # Clear existing syntax tags
            for tag in (
                "keyword", "builtin", "string", "number", "comment",
                "function", "class", "operator", "decorator", "boolean",
                "md_header", "md_bold", "md_italic", "md_code", "md_link", "json_key"
            ):
                self.text_widget.tag_remove(tag, "1.0", "end")
            return

        content = self.text_widget.get("1.0", "end-1c")
        if not content:
            return

        # Precompute line start positions for lightning-fast bisect lookup
        line_starts = [0]
        for m in re.finditer(r"\n", content):
            line_starts.append(m.start() + 1)

        def offset_to_index(pos: int) -> str:
            idx = bisect.bisect_right(line_starts, pos) - 1
            return f"{idx + 1}.{pos - line_starts[idx]}"

        # Clear existing syntax tags
        for tag, _ in self._compiled_rules:
            self.text_widget.tag_remove(tag, "1.0", "end")

        # Track occupied character intervals for strings and comments
        # so keywords inside comments/strings don't get tagged
        mask = [False] * len(content)

        # First pass: comments and strings (heavy containers)
        for tag, regex in self._compiled_rules:
            if tag in ("comment", "string", "md_code"):
                for match in regex.finditer(content):
                    s, e = match.start(), match.end()
                    # If this region is already covered by a prior comment/string, skip
                    if any(mask[s:min(e, s + 50)]):
                        continue
                    for i in range(s, e):
                        if i < len(mask):
                            mask[i] = True
                    start_idx = offset_to_index(s)
                    end_idx = offset_to_index(e)
                    self.text_widget.tag_add(tag, start_idx, end_idx)

        # Second pass: keywords, identifiers, numbers, operators
        for tag, regex in self._compiled_rules:
            if tag not in ("comment", "string", "md_code"):
                for match in regex.finditer(content):
                    # If regex has capture group 1, highlight just group 1 (e.g. def func_name)
                    if match.lastindex and match.lastindex >= 1:
                        s, e = match.start(1), match.end(1)
                    else:
                        s, e = match.start(), match.end()

                    if s < len(mask) and mask[s]:
                        continue

                    start_idx = offset_to_index(s)
                    end_idx = offset_to_index(e)
                    self.text_widget.tag_add(tag, start_idx, end_idx)
