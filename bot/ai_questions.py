import time

import requests

from bot.main import logger


def ask_ai(question):
    """Отправляем запрос к GigaChat API с использованием токена"""
    global access_token, token_expire_time

    if not access_token or time.time() > token_expire_time:
        if not get_gigachat_token():
            return "Сервис временно недоступен. Попробуйте позже."

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    messages = [
        {
            "role": "system",
            "content": (
                "Ты - помощник для ответов пользователей по проектам с сайта VK Education Projects (https://education.vk.company/). Отвечай кратко (1-2 предложения), "
                "используя только информацию с официального сайта VK Education Projects и VK Education. "
                "Если вопросы пользователей не относятся к сайту VK Education, анализируй открытые источники из интернета и предложи посетить сайт VK Education Projects"
                "Будь дружелюбным и полезным. Если вопрос не связан с образовательными проектами VK, "
                "вежливо предложи посетить официальный сайт VK Education Projects. "
                "Не упоминай, что ты ИИ-модель. Используй эмодзи для выразительности. "
                "Проси пользователя переформулировать вопрос, если в его сообщении есть нецензурная брань и предупреждай пользователя о её недопущении."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    data = {
        "model": "GigaChat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=15,
            verify=False
        )

        if response.status_code == 401:
            logger.warning("Токен недействителен. Пробуем обновить...")
            if get_gigachat_token():
                headers['Authorization'] = f'Bearer {access_token}'
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=15,
                    verify=False
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