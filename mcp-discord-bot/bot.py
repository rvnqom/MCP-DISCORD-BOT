# bot.py
import discord
import json
from discord.ext import commands
from modules import filter, transform, route
from utils.helpers import load_rules

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load rules once on startup
rules = load_rules("rules/rules.json")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Apply filters
    if await filter.apply_filters(message, rules.get("filters", [])):
        return  # Message deleted or blocked

    # Apply transformations
    new_content = transform.apply_transformers(message.content, rules.get("transformers", []))
    if new_content != message.content:
        await message.channel.send(f"✏️ Transformed: {new_content}")

    # Route messages
    await route.route_message(bot, message, rules.get("routes", []))

    await bot.process_commands(message)
bot.run("MTA3MDcwMTcwMzQ0MTE2MjM0MQ.GiTdWA.0fcknNSoKcXqzm0n0iHqsQ7SAIh0WwaItzw5cI")

