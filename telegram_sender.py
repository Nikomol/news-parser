#Отправка сообщений в Telegram
import requests
import json
from config import bot_token, chat_id

def shorten_text(text, max_length=900):
    """
    Сокращает текст до max_length символов, обрезая по последнему пробелу или знаку препинания.
    Добавляет многоточие в конце, если текст был сокращён.
    """
    if len(text) <= max_length:
        return text
    
    # Ищем ближайший пробел или знак препинания перед max_length
    last_space = text.rfind(' ', 0, max_length)
    last_punct = max(text.rfind('.', 0, max_length),
                    text.rfind('!', 0, max_length),
                    text.rfind('?', 0, max_length))
    
    cut_pos = max(last_punct, last_space)
    
    if cut_pos == -1 or cut_pos < max_length * 0.7:  # Если не нашли подходящее место
        cut_pos = max_length
    
    shortened = text[:cut_pos].strip()
    if not shortened.endswith(('...', '…')):
        shortened += '... \n \n Полный текст в источнике.'
    
    return shortened

def compose_message(post, is_short=False):
    file_note = "\n\n📎 *В оригинальном посте прикреплён файл.*" if post['has_file'] else ""
    source = f"\n\n🔗 [Источник]({post['link']})"
    
    text = post['text']
    if is_short and len(text) > 300:  # Сокращаем только если текст длинный
        text = shorten_text(text)
    
    return f"\n{text}{file_note}{source}"

def send_to_telegram(post):
    has_media = bool(post['photo_urls'])
    message = compose_message(post, is_short=has_media)

    if post['photo_urls']:
        media = []

        for i, url in enumerate(post['photo_urls']):
            media_item = {
                'type': 'photo',
                'media': url
            }
            if i == 0:
                media_item['caption'] = message
                media_item['parse_mode'] = 'Markdown'
            media.append(media_item)

        response = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMediaGroup',
            data={
                'chat_id': chat_id,
                'media': json.dumps(media)
            }
        )

        if not response.ok:
            print("⚠️ Ошибка отправки медиа-группы:", response.text)

    else:
        # Если нет фото — отправляем обычное сообщение
        response = requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            data={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
        )

        if not response.ok:
            print("⚠️ Ошибка отправки текста:", response.text)