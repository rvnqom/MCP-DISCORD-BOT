import discord
import os
from discord.ext import commands
from modules import filter, transform, route, image_moderation, video_moderation
from utils.helpers import load_rules
from dotenv import load_dotenv

load_dotenv()

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
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 🔍 1. Image Moderation
    if message.attachments:
        for attachment in message.attachments:
            filename = attachment.filename.lower()

            if any(filename.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                if await image_moderation.is_filename_suspicious(filename):
                    await message.delete()
                    await message.channel.send("🚫 Suspicious image filename detected.")
                    return
                if await image_moderation.is_nsfw_image(attachment.url):
                    await message.delete()
                    await message.channel.send("🚫 NSFW image detected.")
                    return

    # 🎞️ 2. Video Moderation
    if await video_moderation.moderate_video_message(message, bot):
        return

    # 💬 3. Text Filtering
    was_filtered = await filter.apply_filters(message, rules.get("filters", []), bot)
    if was_filtered:
        await message.delete()
        await message.channel.send("🚫 Inappropriate text detected.")
        return

    # ✏️ 4. Transformers (replaces content only, no warning)
    new_content = transform.apply_transformers(message.content, rules.get("transformers", []))
    if new_content != message.content:
        await message.channel.send(f"✏️ Transformed: {new_content}")

    # 📦 5. Routing
    await route.route_message(bot, message, rules.get("routes", []))

    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    print("✅ .env Loaded:", bool(token))
    bot.run(token)
