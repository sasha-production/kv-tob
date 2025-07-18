from dotenv import load_dotenv, find_dotenv
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

load_dotenv(find_dotenv())
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
AUTH_KEY = os.getenv("AUTH_KEY_API")
URL_ACCESS_TOKEN = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
URL_GGCHAT_API_FOR_REQUESTS="https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
