import requests
from bs4 import BeautifulSoup
import re

headers = {"User-Agent": "Mozilla/5.0"}

def parse_channel_page(channel):
    url = f'https://t.me/s/{channel}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='tgme_widget_message_wrap')
    return posts[-1] if posts else None

def extract_post_data(post_html, channel):
    text_div = post_html.find('div', class_='tgme_widget_message_text')
    text = text_div.get_text(separator='\n', strip=True) if text_div else '[Без текста]'

    link_tag = post_html.find('a', class_='tgme_widget_message_date')
    post_link = link_tag['href'] if link_tag else ''
    post_id_match = re.search(r'/(\d+)$', post_link)
    post_id = post_id_match.group(1) if post_id_match else None

    # Извлекаем все фото
    photo_divs = post_html.find_all('a', class_='tgme_widget_message_photo_wrap')
    photo_urls = []
    for photo_div in photo_divs:
        if 'style' in photo_div.attrs:
            style = photo_div['style']
            match = re.search(r"url\('(.*?)'\)", style)
            if match:
                photo_urls.append(match.group(1))

    # Признак наличия файла
    has_file = post_html.find('div', class_='tgme_widget_message_document') is not None
    if not has_file and '📎' in text:
        has_file = True

    return {
        'id': post_id,
        'text': text,
        'photo_urls': photo_urls,  # теперь это список всех изображений
        'link': post_link,
        'channel': channel,
        'has_file': has_file
    }
