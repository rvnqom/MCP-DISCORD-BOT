def match_rule(message, rule):
    cond = rule["conditions"]

    if "channel" in cond and message.channel.name != cond["channel"]:
        return False

    if "contains" in cond:
        if not any(word.lower() in message.content.lower() for word in cond["contains"]):
            return False

    if "author_role" in cond:
        roles = [role.name.lower() for role in message.author.roles]
        if cond["author_role"].lower() not in roles:
            return False

    return True
