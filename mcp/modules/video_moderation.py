import cv2
import tempfile
import aiohttp
from PIL import Image
from transformers import pipeline
import os

# Import warning system
from modules.warnings import issue_warning

# Load the Hugging Face NSFW classifier
classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")

async def is_nsfw_video(video_url, confidence_threshold=0.9, scan_interval_seconds=1):
    """
    Scan video for NSFW frames using Hugging Face image classification.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                if resp.status != 200:
                    print("🔴 Video download failed.")
                    return False, None
                video_bytes = await resp.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            print("❌ Failed to open video.")
            return False, None

        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(frame_rate * scan_interval_seconds)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img)
                result = classifier(pil_img)
                print(f"🎞️ Frame {frame_count} classification:", result)

                for label in result:
                    if label["label"].lower() == "nsfw" and label["score"] >= confidence_threshold:
                        cap.release()
                        os.remove(tmp_path)
                        return True, (frame_count, label["score"])

            frame_count += 1

        cap.release()
        os.remove(tmp_path)
        return False, None

    except Exception as e:
        print("⚠️ Error in NSFW video check:", e)
        return False, None


async def moderate_video_message(message, bot):
    """
    Detect and delete NSFW video messages. Notify user, log reason, and issue warning.
    """
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".webm"]):
            detected, info = await is_nsfw_video(attachment.url)
            if detected:
                try:
                    await message.delete()
                except Exception as e:
                    print(f"⚠️ Could not delete message: {e}")
                    return False

                frame, score = info if info else ("unknown", "unknown")

                # Send a visible message in the channel
                await message.channel.send(
                    f"⚠️ {message.author.mention}, your video was removed due to **NSFW content** "
                    f"(Frame `{frame}`, Confidence `{score:.2f}`)."
                )

                # Issue warning via the modular system
                await issue_warning(bot, message.author, message.guild, reason=f"NSFW video (Confidence {score:.2f})")

                return True
    return False
