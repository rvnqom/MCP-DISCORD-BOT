# modules/route.py
async def route_message(bot, message, rules):
    print(f"📦 Routing check: '{message.content}'")  # Debug

    for rule in rules:
        keyword = rule.get("if_contains", "").lower()
        if keyword in message.content.lower():
            print(f"🔁 Route rule match found for keyword: '{keyword}'")  # Debug

            target_channel = bot.get_channel(int(rule["send_to"]))
            if target_channel:
                await target_channel.send(
                    f"📨 Rerouted from {message.channel.mention} by {message.author.mention}:\n{message.content}"
                )
            else:
                print(f"❌ Target channel ID {rule['send_to']} not found")  # Debug

            break  # 🚫 Stop after first match
