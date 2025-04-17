import logging
import os
from dotenv import load_dotenv

load_dotenv()

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    DATABASE_URL = os.environ['DB_URL']
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    ASSISTANT_ID = os.environ['ASSISTANT_ID']
    YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
    TELEGRAM_CHANNEL_ID = os.environ['TELEGRAM_CHANNEL_ID']
    APIFY_TOKEN = os.environ['APIFY_TOKEN']

except KeyError as err:
    logging.critical(f"Can't read token from environment variable. Message: {err}")
    raise KeyError(err)
