import discord
import re
from transformers import pipeline
from modules.warnings import issue_warning, get_warning_count

# Load the hate speech detection model
profanity_detector = pipeline(
    "text-classification",
    model="Hate-speech-CNERG/bert-base-uncased-hatexplain",
    top_k=None
)

# Replace with your actual log channel ID
LOG_CHANNEL_ID = 1352909593763778641

async def apply_filters(message, filters, bot):
    content = message.content.lower()
    detected = False
    detected_bad_words = []

    # Get the sender's name
    sender_name = f"{message.author.name}#{message.author.discriminator}"

    for f in filters:
        if f["type"] in ["pattern", "regex"]:
            pattern = f["pattern"]
            if re.search(pattern, content):
                detected = True
                detected_bad_words.append(f"Regex Match: {pattern}")

        elif f["type"] == "model" and f["name"] == "hate_speech_detection":
            results = profanity_detector(content)
            for result_set in results:
                for result in result_set:
                    label = result["label"].lower()
                    score = result["score"]
                    print(f"🧠 Model result: {result}")
                    if label in ["offensive", "hate speech"] and score > 0.3:
                        detected = True
                        detected_bad_words.append(f"{label} ({score:.2f})")

    if detected:
        try:
            await message.delete()
        except discord.NotFound:
            print("⚠️ Message already deleted.")
        except discord.Forbidden:
            print("🚫 Missing permissions to delete message.")
            return False

        # Issue warning and get warning count
        action_taken = await issue_warning(bot, message.author, message.guild, reason="Inappropriate text content")
        warning_count = await get_warning_count(bot, message.author, message.guild)

        # Notify user with full details
        await message.channel.send(
            f"⚠️ **{sender_name}**, your message was removed due to: {', '.join(detected_bad_words)}\n"
            f"🔢 **Warning Count:** {warning_count}\n"
            f"✅ **Action Taken:** {action_taken}"
        )

        # Log to moderation channel
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"🚫 **Message removed for inappropriate content**\n"
                f"👤 **User:** {sender_name} ({message.author.mention})\n"
                f"💬 **Original Message:** `{message.content}`\n"
                f"⚠️ **Reason:** {', '.join(detected_bad_words)}\n"
                f"🔢 **Warning Count:** {warning_count}\n"
                f"✅ **Action Taken:** {action_taken}"
            )

        return True

    return False
