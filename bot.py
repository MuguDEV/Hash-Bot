"""
A Telegram bot for calculating hash values of text and images.
"""

import os
import hashlib
import asyncio
from typing import Tuple, Optional
import aiofiles
from pyrogram import Client, filters
import configparser

# Load configuration from file
config = configparser.ConfigParser()
config.read("config.ini")

API_ID: Optional[str] = os.environ.get("API_ID") or config.get("telegram", "API_ID", fallback=None)
API_HASH: Optional[str] = os.environ.get("API_HASH") or config.get("telegram", "API_HASH", fallback=None)
BOT_TOKEN: Optional[str] = os.environ.get("BOT_TOKEN") or config.get("telegram", "BOT_TOKEN", fallback=None)

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("Missing API credentials. Please set API_ID, API_HASH, and BOT_TOKEN.")

app: Client = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def calculate_hashes(data: bytes) -> Tuple[str, str, str, str]:
    """
    Calculate SHA-256, MD5, SHA-1, and SHA3-256 hashes for the given data.

    Args:
        data (bytes): The data to calculate hashes for.

    Returns:
        Tuple[str, str, str, str]: A tuple containing the SHA-256, MD5, SHA-1, and SHA3-256 hashes.
    """
    sha256_hash: str = hashlib.sha256(data).hexdigest()
    md5_hash: str = hashlib.md5(data).hexdigest()
    sha1_hash: str = hashlib.sha1(data).hexdigest()
    sha3_256_hash: str = hashlib.sha3_256(data).hexdigest()
    return sha256_hash, md5_hash, sha1_hash, sha3_256_hash

async def handle_text(client: Client, message) -> None:
    """
    Handle text messages by calculating hashes.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    try:
        text: str = message.text
        text_data: bytes = text.encode()
        sha256_hash, md5_hash, sha1_hash, sha3_256_hash = calculate_hashes(text_data)
        response_message: str = (
            f"**SHA-256 Hash:** `{sha256_hash}`\n\n"
            f"**MD5 Hash:** `{md5_hash}`\n\n"
            f"**SHA-1 Hash:** `{sha1_hash}`\n\n"
            f"**SHA3-256 Hash:** `{sha3_256_hash}`"
        )
        await client.send_message(message.chat.id, response_message)
    except (TypeError, ValueError) as e:
        await handle_error(client, message, e)

async def handle_photo(client: Client, message) -> None:
    """
    Handle photo messages by calculating hashes.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    try:
        # Inform the user that the image is being processed
        processing_msg = await client.send_message(message.chat.id, "⌛ Processing image...")

        # Download the photo
        photo_path: str = await client.download_media(message.photo)

        # Read the photo data as bytes
        async with aiofiles.open(photo_path, "rb") as file:
            photo_data: bytes = await file.read()

        sha256_hash, md5_hash, sha1_hash, sha3_256_hash = calculate_hashes(photo_data)

        # Delete the processing message
        await client.delete_messages(message.chat.id, processing_msg.id)

        # Send the hash information
        response_message: str = (
            f"**SHA-256 Hash:** `{sha256_hash}`\n\n"
            f"**MD5 Hash:** `{md5_hash}`\n\n"
            f"**SHA-1 Hash:** `{sha1_hash}`\n\n"
            f"**SHA3-256 Hash:** `{sha3_256_hash}`"
        )
        await client.send_message(message.chat.id, response_message)
    except (TypeError, ValueError) as e:
        await handle_error(client, message, e)
    finally:
        # Delete the downloaded photo file
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)

async def handle_error(client: Client, message, error: Exception) -> None:
    """
    Handle errors by sending a generic error message.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
        error (Exception): The exception raised.
    """
    error_message: str = (
        "An error occurred while processing your request. "
        "Please try again later or contact the bot owner."
    )
    await client.send_message(message.chat.id, error_message)
    # Log the error for further investigation
    print(f"Error: {error}")

@app.on_message(filters.private & filters.command(["start", "help"]))
async def start_help(client: Client, message) -> None:
    """
    Handle the /start and /help commands.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    welcome_message: str = (
        "👋 Welcome! I am your hash value bot.\n\n"
        "Send me text or photos, and I'll provide you with SHA-256 and MD5 hashes. 🚀"
    )
    await client.send_message(message.chat.id, welcome_message)

@app.on_message(filters.private & filters.command("feedback"))
async def feedback_command(client: Client, message) -> None:
    """
    Handle the /feedback command.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    if len(message.text.split(" ")) == 1:
        feedback_message: str = (
        "📣 Feel free to provide your feedback or report any issues with the bot.\n\n"
        "Simply type your feedback, and I'll forward it to the bot owner!\n\n" 
        "Format `/feedback msg`"
    )
        await client.send_message(message.chat.id, feedback_message)
    else:
        feedback_message: str = (
        f"📬 New Feedback from @{message.from_user.username}:\n\n"
        f"{message.text.replace('/feedback','')}"
    )
    # Forward the feedback to the bot owner (you can replace 'owner_user_id' with your user ID)
        await client.send_message(1271659696, feedback_message)
        await client.send_message(message.chat.id, "Thank you for your feedback! 🙏")

@app.on_message(filters.private & filters.text)
async def text_handler(client: Client, message) -> None:
    """
    Handle text messages asynchronously.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    asyncio.create_task(handle_text(client, message))

@app.on_message(filters.private & filters.photo)
async def photo_handler(client: Client, message) -> None:
    """
    Handle photo messages asynchronously.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    asyncio.create_task(handle_photo(client, message))

app.run()
