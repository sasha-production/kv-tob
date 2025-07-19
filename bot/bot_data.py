# bot_data.py
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # корень проекта
BAD_WORDS_FILE_PATH = BASE_DIR / "data" / "forbidden-words.txt"
BAD_WORDS = {w.strip().lower() for w in BAD_WORDS_FILE_PATH.read_text(encoding="utf-8").splitlines() if w.strip()}

_WORD_RE = re.compile(r"[А-Яа-яЁёA-Za-z\-]+")


def contains_bad_words(text: str) -> bool:
    tokens = (w.lower() for w in _WORD_RE.findall(text))
    return any(tok in BAD_WORDS for tok in tokens)

#  Текстовые сообщения
WELCOME_MESSAGE_AFTER_START = (
    "Привет! Я помогу подобрать учебный проект, отвечу на частые вопросы "
    "и покажу контактную информацию.\n\n"
    "Прежде чем задавать вопрос вручную, посмотри 'Частные вопросы'. Там собраны все частые вопросы и ответы на них.\n"
    "Выбери действие ниже 👇"
)

DEFAULT_FALLBACK_MESSAGE = ("Не могу понять что ты имеешь в виду. Переформулируй вопрос или используй кнопки")

ERROR_FALLBACK_MESSAGE = "что-то пошло не так. Попробуй написать 'Старт' "

CONTACTS_TEXT = (
    "Контактная информация:\n"
    "• Пишите, если есть вопросы info@education.vk.company\n"
    "• Сайт VK Education Projects:\n https://education.vk.company/education_projects/\n"

)

BAD_WORDS_WARNING = "Здесь нельзя использовать ненормативную лексику"
