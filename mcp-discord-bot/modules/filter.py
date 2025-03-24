# modules/filter.py
import re
import discord

async def apply_filters(message, rules):
    for rule in rules:
        matched = False

        if rule["type"] == "keyword" and rule["pattern"].lower() in message.content.lower():
            matched = True

        elif rule["type"] == "regex" and re.search(rule["pattern"], message.content):
            matched = True

        if matched:
            try:
                if rule["action"] == "delete":
                    await message.delete()
                    await message.channel.send(f"🚫 Message deleted: {rule.get('reason', 'Violated rule')}")
                elif rule["action"] == "warn":
                    await message.channel.send(f"⚠️ Warning <@{message.author.id}>: inappropriate message.")
            except discord.errors.Forbidden:
                print("[FILTER] Missing permissions.")
            except discord.errors.NotFound:
                print("[FILTER] Message already deleted.")
            return True  # STOP after one match
    return False

