import os
from dotenv import load_dotenv

# Explicitly point to the .env file
dotenv_loaded = load_dotenv(dotenv_path=".env")

# Debug prints
print("✅ .env Loaded:", dotenv_loaded)
print("DISCORD TOKEN:", os.getenv("DISCORD_TOKEN"))


