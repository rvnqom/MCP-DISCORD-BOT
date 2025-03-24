import aiohttp
import tempfile
import os
from PIL import Image
from transformers import pipeline
import discord

# Load Hugging Face NSFW image classification model
classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")

# Suspicious filename keywords
suspicious_keywords = ["nsfw", "nude", "porn", "xxx", "explicit", "sex"]

async def is_filename_suspicious(filename):
    """
    Check if filename contains NSFW-related keywords.
    """
    lowered = filename.lower()
    return any(keyword in lowered for keyword in suspicious_keywords)

async def is_nsfw_image(image_url, confidence_threshold=0.9):
    """
    Check if image content is NSFW.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    print("🔴 Failed to download image.")
                    return False
                img_bytes = await resp.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        image = Image.open(tmp_path).convert("RGB")
        result = classifier(image)

        print(f"🧠 Image classification result: {result}")

        for label in result:
            if label["label"].lower() == "nsfw" and label["score"] >= confidence_threshold:
                os.remove(tmp_path)
                return True

        os.remove(tmp_path)
        return False

    except Exception as e:
        print("⚠️ Error during image NSFW check:", e)
        return False

async def moderate_image_message(message):
    """
    Check image attachment: suspicious filename or NSFW content. Delete if needed.
    """
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            # Check filename
            if await is_filename_suspicious(attachment.filename):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"⚠️ {message.author.mention}, your image was removed due to a suspicious filename."
                    )
                except discord.NotFound:
                    print("⚠️ Tried to delete a message that no longer exists.")
                return True

            # Check image content
            if await is_nsfw_image(attachment.url):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"⚠️ {message.author.mention}, your image was removed due to NSFW content."
                    )
                except discord.NotFound:
                    print("⚠️ Tried to delete a message that no longer exists.")
                return True

    return False
