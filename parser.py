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

def extract_text_with_links(tag):
    parts = []

    prev_was_text = False

    for elem in tag.descendants:
        if elem.name == 'br':
            parts.append('\n')
            prev_was_text = False

        elif elem.name == 'a' and 'href' in elem.attrs:
            text = ''.join(elem.stripped_strings)
            href = elem['href']
            link = f'[{text}]({href})'

            # Добавим пробел перед ссылкой, если предыдущий элемент был текстом и не заканчивается пробелом/переносом
            if parts and not re.search(r'[\s\n]$', parts[-1]):
                parts.append(' ')
            parts.append(link)
            prev_was_text = True

        elif isinstance(elem, str):
            # Добавим пробел после ссылки, если был идущий подряд текст
            if parts and isinstance(parts[-1], str) and not re.search(r'[\s\n]$', parts[-1]):
                parts.append(' ')
            parts.append(elem)
            prev_was_text = True

    # Удалим двойные пробелы
    result = re.sub(r'[ ]{2,}', ' ', ''.join(parts)).strip()

    return result

def postprocess_text_markdown(text):
    # Ссылки уже обработаны. Теперь добавим хештеги и упоминания
    text = re.sub(r'(?<!\w)(@\w+)', r'[\1](https://t.me/\1)', text)
    text = re.sub(r'(?<!\w)(#\w+)', r'[\1](https://t.me/hashtag/\1)', text)
    return text

def extract_post_data(post_html, channel):
    text_div = post_html.find('div', class_='tgme_widget_message_text')
    text = extract_text_with_links(text_div)
    text = postprocess_text_markdown(text)

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
