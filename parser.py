import requests
from bs4 import BeautifulSoup
import time
import re

channel = 'novosti_nsk_test'
url = f'https://t.me/s/{channel}'

bot_token = '1906657023:AAHh5FWI_O0WS1Efhc4kpncny0jJ4zIY0kY'
chat_id = '@parsernsk_test'
headers = {"User-Agent": "Mozilla/5.0"}

def get_latest_post():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='tgme_widget_message_wrap')

    if not posts:
        return None

    last = posts[-1]
    text_div = last.find('div', class_='tgme_widget_message_text')
    text = text_div.get_text(strip=True) if text_div else '[Без текста]'

    # Ищем ID поста
    post_link = last.find('a', class_='tgme_widget_message_date')
    post_href = post_link['href'] if post_link else ''
    post_id_match = re.search(r'/(\d+)$', post_href)
    post_id = post_id_match.group(1) if post_id_match else None

    # Картинка (если есть)
    photo_div = last.find('a', class_='tgme_widget_message_photo_wrap')
    if photo_div and 'style' in photo_div.attrs:
        style = photo_div['style']
        photo_url_match = re.search(r"url\('(.*?)'\)", style)
        photo_url = photo_url_match.group(1) if photo_url_match else None
    else:
        photo_url = None

    return {
        'id': post_id,
        'text': text,
        'photo_url': photo_url,
        'link': post_href
    }

def send_post(post):
    text = f"{post['text']}\n\n🔗 [Источник]({post['link']})"
    if post['photo_url']:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendPhoto',
            data={
                'chat_id': chat_id,
                'photo': post['photo_url'],
                'caption': text,
                'parse_mode': 'Markdown'
            }
        )
    else:
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            data={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
        )

# Первый запуск — просто фиксируем последний пост
latest = get_latest_post()
if latest:
    last_post_id = latest['id']

# Основной цикл
while True:
    #time.sleep(1)
    latest = get_latest_post()
    if latest and latest['id'] != last_post_id:
        send_post(latest)
        last_post_id = latest['id']
