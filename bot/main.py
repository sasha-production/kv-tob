# main.py
import json
import time
import urllib3
import vk_api
from vk_api.bot_longpoll import (
    VkBotLongPoll,
    VkBotEventType,
)
from vk_api.utils import get_random_id
from vk_api.exceptions import ApiError

from bot.config import TOKEN, GROUP_ID
from bot.bot_logic import generate_keyboard_response
from bot.bot_data import ERROR_FALLBACK_MESSAGE, BASE_DIR
from bot.config_logger import logger

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_bot() -> None:
    logger.info("Запуск бота VK Education Projects…")
    logger.info("Успешное соединение c VK API")
    while True:  # Цикл перезапуска при ошибках
        try:
            vk_session = vk_api.VkApi(token=TOKEN)
            vk = vk_session.get_api()
            longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)
            logger.info("LongPoll запущен заново")

            for event in longpoll.listen():
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue
                if not event.from_user:
                    continue

                msg = event.message  # message object
                user_id, raw_text, payload = msg.from_id, (msg.text or "").strip(), None  # user id, text, payload по умолчанию

                if msg.payload:  # Если payload присутствует
                    try:
                        payload = json.loads(msg.payload)
                    except json.JSONDecodeError:
                        logger.warning(f"Не удалось распарсить payload: {msg.payload}")

                logger.info(f"Пользователь {user_id} прислал: '{raw_text}' | payload={payload}")

                if not raw_text and not payload:  # if empty message
                    continue

                try:
                    response_text, keyboard_json = generate_keyboard_response(user_id=user_id, text=raw_text,
                                                                              payload=payload, )
                except Exception as e:
                    logger.exception("Ошибка в generate_keyboard_response: %s", e)
                    response_text, keyboard_json = ERROR_FALLBACK_MESSAGE, None

                if not response_text:  # Если ответ пустой — ничего не шлём
                    continue

                params = {"peer_id": user_id, "message": response_text, "random_id": get_random_id()}

                if keyboard_json:  # При наличии клавиатуры
                    params["keyboard"] = keyboard_json  # Добавляем её в параметры

                try:
                    vk.messages.send(**params)  # Отправляем сообщение
                    logger.info(f"Бот ответил пользователю {user_id}: '{response_text[:60]}'")

                except ApiError as e:  # Ошибка VK API
                    logger.error("VK ApiError при отправке: %s", e)
        except Exception as e:  # Любая критическая ошибка цикла
            logger.error(
                "LongPoll error: %s, перезапуск через 5 сек…", e
            )
            time.sleep(5)  # Пауза


if __name__ == "__main__":
    try:
        run_bot()  # Запуск
    except KeyboardInterrupt:  # остановка Ctrl+C
        logger.info("Бот остановлен")
