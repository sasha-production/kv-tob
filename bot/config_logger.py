import logging
import sys
from logging.handlers import RotatingFileHandler
from bot.bot_data import BASE_DIR


def setup_logger(name):
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования

    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(filename=BASE_DIR / "data" / "bot.logs")
   # RotatingFileHandler - ротация по размеру файла
    file_handler = RotatingFileHandler(
        filename=BASE_DIR / "data" / "bot.logs",
        maxBytes=1024*1024,  # 1 MB
        backupCount=1,  # сохранять 1 резервных копий
        encoding='utf-8'
    ) 
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)

    return logger


# Создаем корневой логгер
logger = setup_logger(__name__)
