import os
import hashlib
import asyncio
import aiofiles
from pyrogram import Client, filters

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def calculate_hashes(data):
    sha256_hash = hashlib.sha256(data).hexdigest()
    md5_hash = hashlib.md5(data).hexdigest()
    return sha256_hash, md5_hash

async def handle_text(client, message):
    try:
        text = message.text
        sha256_hash, md5_hash = calculate_hashes(text.encode())
        response_message = (
            f"**SHA-256 Hash:** `{sha256_hash}`\n\n"
            f"**MD5 Hash:** `{md5_hash}`"
        )
        await client.send_message(message.chat.id, response_message)
    except Exception as e:
        await handle_error(client, message, e)


async def handle_photo(client, message):
    try:
        # Inform the user that the image is being processed
        processing_msg = await client.send_message(message.chat.id, "⌛ Processing image...")
        
        # Download the photo
        photo_path = await client.download_media(message.photo)

        # Read the photo data as bytes
        async with aiofiles.open(photo_path, "rb") as file:
            photo_data = await file.read()

        sha256_hash, md5_hash = calculate_hashes(photo_data)

        # Delete the processing message
        await client.delete_messages(message.chat.id, processing_msg.id)

        # Send the hash information
        response_message = (
            f"**SHA-256 Hash for photo:** `{sha256_hash}`\n\n"
            f"**MD5 Hash for photo:** `{md5_hash}`"
        )
        await client.send_message(message.chat.id, response_message)
    except Exception as e:
        await handle_error(client, message, e)
    finally:
        # Delete the downloaded photo file
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)


async def handle_error(client, message, error):
    error_message = (
        "An error occurred while processing your request. "
        "Please try again later or contact the bot owner."
    )
    await client.send_message(message.chat.id, error_message)
    # Log the error for further investigation
    print(f"Error: {error}")

@app.on_message(filters.private & filters.command(["start", "help"]))
async def start_help(client, message):
    welcome_message = (
        "👋 Welcome! I am your hash value bot.\n\n"
        "Send me text or photos, and I'll provide you with SHA-256 and MD5 hashes. 🚀"
    )
    await client.send_message(message.chat.id, welcome_message)

@app.on_message(filters.private & filters.command("feedback"))
async def feedback_command(client, message):
    if len(message.text.split(" "))== 1:
        feedback_message = (
        "📣 Feel free to provide your feedback or report any issues with the bot.\n\n"
        "Simply type your feedback, and I'll forward it to the bot owner!\n\n" 
        "Format `/feedback msg`"
    )
        await client.send_message(message.chat.id, feedback_message)
    else:
        feedback_message = (
        f"📬 New Feedback from @{message.from_user.username}:\n\n"
        f"{message.text.replace('/feedback','')}"
    )
    # Forward the feedback to the bot owner (you can replace 'owner_user_id' with your user ID)
        await client.send_message(1271659696, feedback_message)
        await client.send_message(message.chat.id, "Thank you for your feedback! 🙏")

@app.on_message(filters.private & filters.text)
async def text_handler(client, message):
    # Handle text asynchronously
    asyncio.create_task(handle_text(client, message))

@app.on_message(filters.private & filters.photo)
async def photo_handler(client, message):
    # Handle photo asynchronously
    asyncio.create_task(handle_photo(client, message))

app.run()
