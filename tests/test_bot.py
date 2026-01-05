import os
import pytest
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from pyrogram import Client
from pyrogram.types import Message
from bot import calculate_hashes, handle_text, handle_photo, handle_error, check_virustotal

@pytest.fixture
def client():
    # Mock the Client to avoid actual Telegram connections
    # Using simple MagicMock for Client as we only need to mock methods like send_message
    app = MagicMock()
    return app

def test_calculate_hashes():
    data = b"test data"
    sha256_hash, md5_hash, sha1_hash, sha3_256_hash = calculate_hashes(data)
    assert sha256_hash == hashlib.sha256(data).hexdigest()
    assert md5_hash == hashlib.md5(data).hexdigest()
    assert sha1_hash == hashlib.sha1(data).hexdigest()
    assert sha3_256_hash == hashlib.sha3_256(data).hexdigest()

@pytest.mark.asyncio
async def test_handle_text(client):
    message = MagicMock()
    message.text = "test text"
    message.chat.id = 12345

    # Mock send_message to be an async function
    client.send_message = AsyncMock()

    await handle_text(client, message)

    # Verify send_message was called
    client.send_message.assert_called_once()
    args, _ = client.send_message.call_args
    assert args[0] == 12345
    assert "**SHA-256 Hash:**" in args[1]

@pytest.mark.asyncio
async def test_handle_photo(client):
    message = MagicMock()
    message.photo = MagicMock()
    message.chat.id = 12345

    # Mocking
    client.send_message = AsyncMock(return_value=MagicMock(id=999))
    client.download_media = AsyncMock(return_value="test_photo.jpg")
    client.delete_messages = AsyncMock()

    # Mock aiofiles.open using patch
    with patch("aiofiles.open") as mock_open, \
         patch("os.remove") as mock_remove, \
         patch("os.path.exists", return_value=True):

        mock_file = AsyncMock()
        mock_file.read.return_value = b"fake photo data"
        mock_open.return_value.__aenter__.return_value = mock_file

        await handle_photo(client, message)

        # Verify interactions
        client.download_media.assert_called_once_with(message.photo)
        client.send_message.assert_called() # Called twice (processing + result)
        assert client.send_message.call_count == 2

        # Check if hash was calculated correctly for "fake photo data"
        expected_sha256 = hashlib.sha256(b"fake photo data").hexdigest()
        expected_md5 = hashlib.md5(b"fake photo data").hexdigest()
        result_message = client.send_message.call_args_list[1][0][1]
        assert expected_sha256 in result_message

        # Check if button was added (reply_markup present)
        kwargs = client.send_message.call_args_list[1][1]
        assert "reply_markup" in kwargs

        # Verify MD5 is used in callback data
        reply_markup = kwargs["reply_markup"]
        # Accessing InlineKeyboardMarkup.inline_keyboard[0][0].callback_data
        callback_data = reply_markup.inline_keyboard[0][0].callback_data
        assert f"vt_{expected_md5}" == callback_data

@pytest.mark.asyncio
async def test_check_virustotal():
    file_hash = "dummy_hash"

    # Mock aiohttp.ClientSession
    with patch("aiohttp.ClientSession") as MockSession:
        # MockSession() returns an async context manager
        mock_session_ctx = MagicMock()
        MockSession.return_value = mock_session_ctx

        # The session object yielded by the context manager
        mock_session = MagicMock()
        mock_session_ctx.__aenter__.return_value = mock_session
        mock_session_ctx.__aexit__.return_value = AsyncMock() # awaitable

        # Mock the response object
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 0,
                        "harmless": 50,
                        "undetected": 10
                    }
                }
            }
        }

        # session.get() returns an async context manager
        mock_get_ctx = MagicMock()
        mock_session.get.return_value = mock_get_ctx
        mock_get_ctx.__aenter__.return_value = mock_response
        mock_get_ctx.__aexit__.return_value = AsyncMock() # awaitable

        # Case 1: Clean
        result = await check_virustotal(file_hash)
        assert "✅ Clean" in result

        # Case 2: Malicious
        mock_response.json.return_value = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 5,
                        "harmless": 45,
                        "undetected": 10
                    }
                }
            }
        }
        result = await check_virustotal(file_hash)
        assert "⚠️ Detected (5/60)" in result

@pytest.mark.asyncio
async def test_handle_error(client):
    message = MagicMock()
    message.chat.id = 12345
    error = ValueError("Test error")

    client.send_message = AsyncMock()

    await handle_error(client, message, error)

    client.send_message.assert_called_once()
    assert "An error occurred" in client.send_message.call_args[0][1]
