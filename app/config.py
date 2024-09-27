import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

TORTOISE_ORM = {
    "connections": {
        "default": DB_URL
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    }
}
