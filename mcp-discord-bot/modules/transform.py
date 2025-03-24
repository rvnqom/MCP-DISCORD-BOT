import re

def apply_transformers(content, transformers):
    """
    Applies transformation rules to a given message content.
    :param content: str - the original message content
    :param transformers: list - list of transformation rules from rules.json
    :return: str - transformed content
    """
    original_content = content

    for t in transformers:
        t_type = t.get("type", "replace").lower()

        if t_type == "replace":
            target = t.get("target")
            replacement = t.get("replacement", "")
            if target:
                content = content.replace(target, replacement)

        elif t_type == "regex_replace":
            pattern = t.get("pattern")
            replacement = t.get("replacement", "")
            if pattern:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        else:
            print(f"⚠️ Unknown transformer type: {t_type}")

    if original_content != content:
        print(f"🔄 Transformed: '{original_content}' → '{content}'")

    return content

