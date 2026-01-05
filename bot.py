"""
A Telegram bot for calculating hash values of text and images.
"""

import os
import hashlib
import asyncio
from typing import Tuple, Optional
import aiofiles
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import configparser

# Load configuration from file
config = configparser.ConfigParser()
config.read("config.ini")

API_ID: Optional[str] = os.environ.get("API_ID") or config.get("telegram", "API_ID", fallback=None)
API_HASH: Optional[str] = os.environ.get("API_HASH") or config.get("telegram", "API_HASH", fallback=None)
BOT_TOKEN: Optional[str] = os.environ.get("BOT_TOKEN") or config.get("telegram", "BOT_TOKEN", fallback=None)
VIRUSTOTAL_API_KEY: Optional[str] = os.environ.get("VIRUSTOTAL_API_KEY") or config.get("virustotal", "API_KEY", fallback=None)

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

async def check_virustotal(file_hash: str) -> str:
    """
    Check the file hash against VirusTotal API.

    Args:
        file_hash (str): The SHA-256 hash of the file.

    Returns:
        str: A message with the scan result.
    """
    if not VIRUSTOTAL_API_KEY:
        return "⚠️ VirusTotal API Key is not configured."

    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data["data"]["attributes"]["last_analysis_stats"]
                    malicious = stats["malicious"]
                    total = sum(stats.values())

                    if malicious == 0:
                        return f"✅ Clean ({malicious}/{total})"
                    else:
                        return f"⚠️ Detected ({malicious}/{total})"
                elif response.status == 404:
                    return "ℹ️ Hash not found in VirusTotal."
                else:
                    return f"❌ Error contacting VirusTotal (Status: {response.status})."
    except Exception as e:
        return f"❌ Error: {str(e)}"

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

        # Add VirusTotal Button
        # Using MD5 because callback_data limit is 64 bytes. SHA256 is 64 chars + prefix > 64.
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡 Check VirusTotal", callback_data=f"vt_{md5_hash}")]
        ])

        await client.send_message(message.chat.id, response_message, reply_markup=keyboard)
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
        "Send me text or photos, and I'll provide you with SHA-256 and MD5 hashes. 🚀\n\n"
        "Commands:\n"
        "/verify <hash> - Verify if a hash matches the replied message."
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

@app.on_message(filters.private & filters.command("verify"))
async def verify_command(client: Client, message) -> None:
    """
    Handle the /verify command.

    Args:
        client (Client): The Pyrogram client.
        message: The message object.
    """
    if not message.reply_to_message or not message.reply_to_message.text:
        await client.send_message(message.chat.id, "⚠️ Please reply to a message containing the hash you want to verify.")
        return

    try:
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await client.send_message(message.chat.id, "⚠️ Usage: `/verify <hash_to_check>`")
            return

        user_hash = command_parts[1].strip().lower()
        original_text = message.reply_to_message.text.lower()

        if user_hash in original_text:
            await client.send_message(message.chat.id, "✅ Match found! The hash corresponds to the message.")
        else:
            await client.send_message(message.chat.id, "❌ No match found.")

    except Exception as e:
        await handle_error(client, message, e)

@app.on_callback_query(filters.regex(r"^vt_"))
async def handle_vt_callback(client: Client, callback_query: CallbackQuery) -> None:
    """
    Handle VirusTotal check callback.
    """
    file_hash = callback_query.data.split("_")[1]

    await callback_query.answer("🔍 Checking VirusTotal...", show_alert=False)

    try:
        result = await check_virustotal(file_hash)
        await callback_query.answer(result, show_alert=True)
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

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

if __name__ == "__main__":
    app.run()
