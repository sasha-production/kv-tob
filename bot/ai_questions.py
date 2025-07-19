import time
import uuid
from pathlib import Path

import requests
from bot.config_logger import logger
from bot.config import URL_ACCESS_TOKEN, URL_GGCHAT_API_FOR_REQUESTS, AUTH_KEY

access_token = None
token_expire_time = 0

BASE_DIR = Path(__file__).resolve().parent.parent  # корень проекта
CERT = BASE_DIR / "chain.pem"

def get_access_token():
    """
    Получаем Access token
    Чтобы иметь возможность отправлять авторизованные запросы к API
    """
    global access_token, token_expire_time

    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {AUTH_KEY}'
    }

    try:
        response = requests.post(URL_ACCESS_TOKEN, headers=headers, data=payload, timeout=10, verify=CERT
                                 )

        if response.status_code == 200:
            data = response.json()
            access_token = data['access_token']
            token_expire_time = time.time() + 25 * 60
            logger.info("Токен GigaChat успешно получен")
            return True
        else:
            logger.error(f"Ошибка получения токена: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при получении токена: {str(e)}")
        return False


def ask_ai(question_message):
    """Отправляем запрос к GigaChat API с использованием токена"""
    global access_token, token_expire_time

    if not access_token or time.time() > token_expire_time:
        if not get_access_token():
            return "Сервис временно недоступен. Попробуй найти нужную информацию в частых вопросах и/или проанализировав проекты"

    url = URL_GGCHAT_API_FOR_REQUESTS
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    messages = [
        {
            "role": "system",
            "content": (
                "Ты - помощник для ответов пользователей по вопросам, связанных с сервисом VK Education Projects (https://education.vk.company/education_projects). Отвечай кратко (1-2 предложения), "
                "используя только информацию с официального сайта VK Education Projects. "
                "Если вопросы пользователей не относятся к VK Education Projects, анализируй открытые источники из интернета и предложи посетить сайт VK Education Projects"
                "Будь дружелюбным и полезным. Если вопрос не связан с образовательными проектами VK, "
                "вежливо предложи посетить официальный сайт VK Education Projects. "
                "Не упоминай, что ты ИИ-модель. Используй эмодзи для выразительности. "
                "Проси пользователя переформулировать вопрос, если в его сообщении есть нецензурная брань и предупреждай пользователя о её недопущении."
            )
        },
        {
            "role": "user",
            "content": question_message
        }
    ]

    data = {
        "model": "GigaChat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 250
    }

    try:
        # response = requests.request("GET", url, headers=headers, data=data, verify=False, timeout=15)
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=15,
            verify=CERT
        )

        if response.status_code == 401:
            logger.warning("Токен недействителен. Пробуем обновить...")
            if get_access_token():
                headers['Authorization'] = f'Bearer {access_token}'
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=15,
                    verify=CERT
                )
            else:
                return "Ошибка авторизации. Попробуйте позже."

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"Ошибка API GigaChat: {response.status_code}, {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.warning("Таймаут при запросе к GigaChat API")
        return None
    except Exception as e:
        logger.error(f"Ошибка запроса к GigaChat: {str(e)}")
        return None

if __name__ == "__main__":
    print(ask_ai(question_message="что такое vk education projects и сколько проектов можно выбрать"))