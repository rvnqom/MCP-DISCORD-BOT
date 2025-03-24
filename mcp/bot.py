from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import discord
import os
from discord.ext import commands
from modules import filter, transform, route, image_moderation, video_moderation
from utils.helpers import load_rules
from dotenv import load_dotenv

load_dotenv()

LOG_SERVER_URL = "http://192.168.128.238:8080/logs"  # Flask server for logging

def log_to_backend(log_type, message, sender="Unknown"):
    """Logs moderation events to Flask backend."""
    log_entry = {
        "log_type": log_type,
        "message": message,
        "sender": sender
    }
    try:
        response = requests.post(LOG_SERVER_URL, json=log_entry)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Log failed: {e}")  # Debugging log failures

# 🔥 Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

rules = load_rules("rules/rules.json")

@bot.event
async def on_ready():
    log_to_backend("INFO", f"✅ Logged in as {bot.user}")
    print(f"✅ Logged in as {bot.user}")

async def moderate_message(message):
    """Handles moderation for messages (text, image, video)."""
    if message.author.bot:
        return

    sender_name = f"{message.author.name}#{message.author.discriminator}"

    try:
        # 🔍 Image Moderation
        if await image_moderation.moderate_image_message(message):
            log_to_backend("IMAGE_MOD", f"🖼️ NSFW or suspicious image removed", sender_name)
            return

        # 🎞️ Video Moderation
        if await video_moderation.moderate_video_message(message, bot):
            log_to_backend("VIDEO_MOD", f"🎥 Inappropriate video removed", sender_name)
            return

        # 💬 Text Filtering
        was_filtered = await filter.apply_filters(message, rules.get("filters", []), bot)
        if was_filtered:
            log_to_backend("TEXT_FILTER", f"🚫 Inappropriate text removed", sender_name)
            return

        # ✏️ Transformers (Soft content changes)
        new_content = transform.apply_transformers(message.content, rules.get("transformers", []))
        if new_content != message.content:
            await message.channel.send(f"✏️ Transformed: {new_content}")
            log_to_backend("TEXT_TRANSFORM", f"🔄 Transformed message: {new_content}", sender_name)

        # 📦 Message Routing
        routed = await route.route_message(bot, message, rules.get("routes", []))
        if routed:
            log_to_backend("MESSAGE_ROUTE", f"📤 Message routed to another channel", sender_name)

    except Exception as e:
        print(f"⚠️ Error in moderation: {e}")
        log_to_backend("ERROR", f"Moderation error: {e}", sender_name)

@bot.event
async def on_message(message):
    """Processes incoming messages."""
    await moderate_message(message)
    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN is missing in .env file!")
    else:
        print(f"✅ .env Loaded: {bool(token)}")
        bot.run(token)
