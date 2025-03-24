import aiohttp
import tempfile
import os
from PIL import Image
from transformers import pipeline
import discord
from utils.logger import log_to_backend  # Import logging utility

# Load Hugging Face NSFW image classification model
classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")

# Suspicious filename keywords
SUSPICIOUS_KEYWORDS = {"nsfw", "nude", "porn", "xxx", "explicit", "sex"}

async def is_filename_suspicious(filename):
    """
    Check if the filename contains NSFW-related keywords.
    """
    return any(keyword in filename.lower() for keyword in SUSPICIOUS_KEYWORDS)

async def is_nsfw_image(image_url, confidence_threshold=0.9):
    """
    Check if an image is NSFW based on its content.
    """
    tmp_path = None
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
        results = classifier(image)

        print(f"🧠 Image classification result: {results}")

        for label in results:
            if label["label"].lower() == "nsfw" and label["score"] >= confidence_threshold:
                log_to_backend("IMAGE_MOD", f"NSFW detected ({label['score']*100:.2f}%)", "System")
                return True

        return False

    except Exception as e:
        print("⚠️ Error during NSFW image check:", e)
        return False

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)  # Clean up temp file

async def moderate_image_message(message):
    """
    Checks image attachments for NSFW content or suspicious filenames.
    Deletes and warns the user if necessary.
    """
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            sender_name = f"{message.author.name}#{message.author.discriminator}"

            # 🔍 Check filename
            if await is_filename_suspicious(attachment.filename):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"⚠️ {message.author.mention}, your image was removed due to a suspicious filename."
                    )
                    log_to_backend("IMAGE_MOD", f"Suspicious filename detected: {attachment.filename}", sender_name)
                except discord.NotFound:
                    print("⚠️ Tried to delete a message that no longer exists.")
                return True

            # 🔍 Check NSFW content
            if await is_nsfw_image(attachment.url):
                try:
                    await message.delete()
                    await message.channel.send(
                        f"🚫 {message.author.mention}, your image was removed due to NSFW content."
                    )
                    log_to_backend("IMAGE_MOD", "NSFW image detected and removed", sender_name)
                except discord.NotFound:
                    print("⚠️ Tried to delete a message that no longer exists.")
                return True

    return False
