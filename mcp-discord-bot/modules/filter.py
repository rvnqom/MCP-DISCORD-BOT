import discord
import re
from transformers import pipeline

# Load the hate speech detection model
profanity_detector = pipeline(
    "text-classification",
    model="Hate-speech-CNERG/bert-base-uncased-hatexplain",
    top_k=None
)

LOG_CHANNEL_ID = 1352909593763778641  # Change if needed

async def apply_filters(message, filters, bot):
    content = message.content.lower()
    detected = False
    detected_bad_words = []

    for f in filters:
        if f["type"] == "pattern" or f["type"] == "regex":
            pattern = f["pattern"]
            if re.search(pattern, content):
                detected = True
                detected_bad_words.append(pattern)

        elif f["type"] == "model" and f["name"] == "hate_speech_detection":
            results = profanity_detector(content)

            for result_set in results:  # result_set is a list of dicts
                for result in result_set:
                    label = result["label"].lower()
                    score = result["score"]
                    print(f"🧠 Model result: {result}")
                    if label in ["offensive", "hate speech"] and score > 0.3:
                        detected = True
                        detected_bad_words.append(f"{label} ({score:.2f})")

    if detected:
        await message.delete()

        # Log the moderation action
        log_channel = bot.get_channel(1352909593763778641)
        if log_channel:
            await log_channel.send(
                f"🚫 **Message removed for inappropriate content**\n"
                f"👤 User: {message.author.mention}\n"
                f"💬 Content: `{content}`\n"
                f"⚠️ Reason: {', '.join(detected_bad_words)}"
            )

        # Optional: Notify user
        await message.channel.send(
            f"⚠️ {message.author.mention}, your message was removed due to: {', '.join(detected_bad_words)}"
        )

        return True

    return False
