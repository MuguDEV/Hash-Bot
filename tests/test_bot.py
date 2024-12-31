import os
import pytest
from pyrogram import Client
from pyrogram.types import Message
from bot import calculate_hashes, handle_text, handle_photo, handle_error

@pytest.fixture
def client():
    app = Client("test_bot")
    yield app
    app.stop()

@pytest.mark.asyncio
async def test_calculate_hashes():
    data = b"test data"
    sha256_hash, md5_hash, sha1_hash, sha3_256_hash = calculate_hashes(data)
    assert sha256_hash == hashlib.sha256(data).hexdigest()
    assert md5_hash == hashlib.md5(data).hexdigest()
    assert sha1_hash == hashlib.sha1(data).hexdigest()
    assert sha3_256_hash == hashlib.sha3_256(data).hexdigest()

@pytest.mark.asyncio
async def test_handle_text(client):
    message = Message(text="test text")
    await handle_text(client, message)
    # Add assertions to verify the expected behavior

@pytest.mark.asyncio
async def test_handle_photo(client):
    message = Message(photo="test_photo.jpg")
    await handle_photo(client, message)
    # Add assertions to verify the expected behavior

@pytest.mark.asyncio
async def test_handle_error(client):
    message = Message(text="test error")
    error = ValueError("Test error")
    await handle_error(client, message, error)
    # Add assertions to verify the expected behavior
