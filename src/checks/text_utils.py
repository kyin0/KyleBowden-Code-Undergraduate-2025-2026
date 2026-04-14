def find_matching_paren(text: str, open_index: int) -> int:
    depth = 1
    in_string = False
    string_char = ""
    escaped = False
    cursor = open_index + 1

    while cursor < len(text):
        char = text[cursor]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == string_char:
                in_string = False
        else:
            if char == '"' or char == "'":
                in_string = True
                string_char = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1

                if depth == 0:
                    return cursor

        cursor += 1

    return -1


def split_top_level(text: str) -> list[str]:
    parts = []
    current = []
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string = False
    string_char = ""
    escaped = False

    for char in text:
        if in_string:
            current.append(char)

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == string_char:
                in_string = False

            continue

        if char == '"' or char == "'":
            in_string = True
            string_char = char
            current.append(char)
            continue

        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1

        if char == "," and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
            part = "".join(current).strip()

            if part:
                parts.append(part)

            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()

    if tail:
        parts.append(tail)

    return parts


def contains_token(text: str, token: str) -> bool:
    index = 0

    while True:
        marker = text.find(token, index)

        if marker == -1:
            return False

        left_ok = marker == 0 or (not text[marker - 1].isalnum() and text[marker - 1] != "_")
        end = marker + len(token)
        right_ok = end >= len(text) or (not text[end].isalnum() and text[end] != "_")

        if left_ok and right_ok:
            return True

        index = marker + 1


def extract_call_inners(code: str, name: str) -> list[str]:
    token = f"{name}("
    start = 0
    calls = []

    while True:
        marker = code.find(token, start)

        if marker == -1:
            return calls

        close_index = find_matching_paren(code, marker + len(name))

        if close_index == -1:
            return calls

        calls.append(code[marker + len(token):close_index])
        start = close_index + 1


def literal_string(text: str):
    normalized = text.strip()

    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {'"', "'"}:
        return normalized[1:-1]

    return None


def collect_plan_functions(code: str) -> list[dict]:
    lines = code.splitlines()
    plans = []
    pending_decorator = None
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()

        if stripped.startswith("@pl("):
            decorator, index = _collect_parenthesized_block(lines, index, "@pl(")
            pending_decorator = decorator
            continue

        if pending_decorator and stripped.startswith("def "):
            signature, next_index = _collect_def_signature(lines, index)
            name = _extract_function_name(signature)
            param_count = _count_parameters(signature)
            body, body_end = _collect_function_body(lines, index)

            if name is not None:
                plans.append(
                    {
                        "name": name,
                        "decorator": pending_decorator,
                        "parameter_count": param_count,
                        "body": body,
                    }
                )

            pending_decorator = None
            index = max(next_index, body_end)
            continue

        if stripped and not stripped.startswith("@"):
            pending_decorator = None

        index += 1

    return plans


def _collect_parenthesized_block(lines: list[str], start_index: int, prefix: str) -> tuple[str, int]:
    first = lines[start_index].strip()
    text = first[len(prefix):]
    depth = 1
    index = start_index

    while index < len(lines):
        segment = text if index == start_index else lines[index].strip()
        depth += segment.count("(")
        depth -= segment.count(")")

        if depth <= 0:
            break

        index += 1

        if index < len(lines):
            text += " " + lines[index].strip()

    if ")" in text:
        text = text.rsplit(")", 1)[0]

    return text.strip(), index + 1


def _collect_def_signature(lines: list[str], start_index: int) -> tuple[str, int]:
    text = lines[start_index].strip()
    index = start_index + 1

    while index < len(lines) and ":" not in text:
        text += " " + lines[index].strip()
        index += 1

    return text, index


def _extract_function_name(signature: str):
    after_def = signature[4:] if signature.startswith("def ") else signature
    open_paren = after_def.find("(")

    if open_paren == -1:
        return None

    return after_def[:open_paren].strip()


def _count_parameters(signature: str) -> int:
    open_paren = signature.find("(")
    close_paren = signature.rfind(")")

    if open_paren == -1 or close_paren == -1 or close_paren <= open_paren:
        return 0

    params_text = signature[open_paren + 1:close_paren]

    if not params_text.strip():
        return 0

    return len(split_top_level(params_text))


def _collect_function_body(lines: list[str], def_index: int) -> tuple[str, int]:
    def_line = lines[def_index]
    def_indent = len(def_line) - len(def_line.lstrip())
    index = def_index + 1
    body_lines = []

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped:
            indent = len(line) - len(line.lstrip())

            if indent <= def_indent:
                break

        body_lines.append(line)
        index += 1

    return "\n".join(body_lines), index