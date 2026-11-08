"""ИИ-часть: превращает текст продавца в данные. Цены ИИ не считает."""
import json

from google import genai

PROMPT = """Ты помощник логистического сайта. Из сообщения продавца достань данные.
Верни только JSON:
{"cargo_type": "одежда" | "продукты" | "стройматериалы" | "электроника" | "другое" | null,
 "weight_kg": число или null,
 "from_city": строка или null,
 "to_city": строка или null}
Если чего-то нет в сообщении, ставь null. Ничего не придумывай.
Сообщение продавца: """

BACKUP_MODEL = "gemini-3.1-flash-lite"  # запасная модель, если основная перегружена


def parse_request(text, api_key, model="gemini-3.1-flash-lite"):
    """Пробует основную модель, потом запасную. Если обе недоступны — None."""
    client = genai.Client(api_key=api_key)
    for name in [model, BACKUP_MODEL]:
        try:
            response = client.models.generate_content(
                model=name,
                contents=PROMPT + text,
                config={"response_mime_type": "application/json"},  # ответ строго в JSON
            )
            return json.loads(response.text)
        except Exception as e:
            print("ОШИБКА ИИ:", name, e)  # причина ошибки видна в терминале
    return None  # сайт продолжит работать: пользователь заполнит форму сам
    