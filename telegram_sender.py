#Отправка сообщений в Telegram
import requests
import json

bot_token = '1906657023:AAHh5FWI_O0WS1Efhc4kpncny0jJ4zIY0kY'
chat_id = '@parsernsk_test'

def compose_message(post):
    file_note = "\n\n📎 *В оригинальном посте прикреплён файл.*" if post['has_file'] else ""
    source = f"\n\n🔗 [Источник]({post['link']})"
    return f"\n{post['text']}{file_note}{source}"

def send_to_telegram(post):
    message = compose_message(post)

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