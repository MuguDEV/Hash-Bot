# Telegram Hash Bot 

[![Pylint](https://github.com/MuguDEV/Hash-Bot/actions/workflows/pylint.yml/badge.svg)](https://github.com/MuguDEV/Hash-Bot/actions/workflows/pylint.yml)

[![CodeQL](https://github.com/MuguDEV/Hash-Bot/actions/workflows/codeql.yml/badge.svg)](https://github.com/MuguDEV/Hash-Bot/actions/workflows/codeql.yml)

🚀 Calculate SHA-256 and MD5 hashes for text and photos on Telegram with this simple and secure Python bot!


## Features
- **Text Hashing:** Send any text message, and the bot will provide SHA-256 and MD5 hashes.
- **Photo Hashing:** Upload photos, and the bot will calculate hashes for the photo data.
- **User Feedback:** Use the `/feedback` command to provide feedback or report issues.

## Getting Started
1. Clone the repository: `git clone https://github.com/MuguDEV/Hash-Bot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your Telegram API credentials in the code.
4. Run the bot: `python3 bot.py`

## Configuration
- `API_ID`: Your Telegram API ID.
- `API_HASH`: Your Telegram API hash.
- `BOT_TOKEN`: Your Telegram bot token.

## Requirements
- Python 3.7+
- [Pyrogram](https://docs.pyrogram.org/)
- [Aiofiles](https://github.com/Tinche/aiofiles)
- [TgCrypto](https://github.com/pyrogram/tgcrypto)

## Usage
- Start the bot and send messages or photos to calculate hashes.
- Use the `/feedback` command to provide feedback or report issues.

## Contributing
Feel free to contribute, report issues, or suggest improvements! Your feedback is highly appreciated.

## Setting up Telegram API credentials
To set up the Telegram API credentials, follow these steps:

1. Go to [my.telegram.org](https://my.telegram.org) and log in with your Telegram account.
2. Click on "API Development Tools" and create a new application.
3. Note down the `API_ID` and `API_HASH` provided.
4. Create a new bot on Telegram by talking to the [BotFather](https://t.me/botfather) and note down the `BOT_TOKEN`.

## Deployment
To deploy the bot, you can use platforms like Heroku, Railway, or any other cloud service provider. Here are the steps to deploy on Railway:

1. Sign up for a Railway account at [railway.app](https://railway.app).
2. Create a new project and link your GitHub repository.
3. Set the environment variables `API_ID`, `API_HASH`, and `BOT_TOKEN` in the Railway project settings.
4. Deploy the project.

## Badges
[![Dependency Review](https://github.com/MuguDEV/Hash-Bot/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/MuguDEV/Hash-Bot/actions/workflows/dependency-review.yml)

Happy hashing! 🚀
