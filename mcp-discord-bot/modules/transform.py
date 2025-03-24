def apply_transformers(content, transformers):
    original = content
    for t in transformers:
        if t["type"] == "replace":
            content = content.replace(t["target"], t["replacement"])
    if content != original:
        print(f"✏️ Transformed: '{original}' → '{content}'")  # Debug
    return content
