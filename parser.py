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
    if not tag:
        return ""
    
    parts = []
    processed_elements = set()  # Для отслеживания уже обработанных элементов

    for elem in tag.children:
        if id(elem) in processed_elements:
            continue
        processed_elements.add(id(elem))

        if elem.name == 'br':
            parts.append('\n')
        elif elem.name == 'a' and 'href' in elem.attrs:
            text = ''.join(elem.stripped_strings)
            href = elem['href']
            link = f'[{text}]({href})' if text != href else href
            
            if parts and not parts[-1].endswith(('\n', ' ')):
                parts.append(' ')
            parts.append(link)
        elif isinstance(elem, str):
            text = elem.strip()
            if text:
                if parts and not parts[-1].endswith(('\n', ' ')):
                    parts.append(' ')
                parts.append(text)
        else:
            # Рекурсивная обработка вложенных элементов
            nested_text = extract_text_with_links(elem)
            if nested_text:
                if parts and not parts[-1].endswith(('\n', ' ')):
                    parts.append(' ')
                parts.append(nested_text)

    result = ''.join(parts).strip()
    result = re.sub(r'[ ]{2,}', ' ', result)
    return result

def postprocess_text_markdown(text):
    # Удаляем голые @username, если они не являются частью ссылки
    text = re.sub(r'(?<!\w)@(\w+)(?![^[]*\])', '', text)
    # Оставляем хештеги как есть (они не должны дублироваться после extract_text_with_links)
    return text

def extract_post_data(post_html, channel):
    # Обработка текста (с проверкой на None)
    text_div = post_html.find('div', class_='tgme_widget_message_text')
    text = extract_text_with_links(text_div) if text_div else "[]"
    text = postprocess_text_markdown(text)

    # Остальной код без изменений
    link_tag = post_html.find('a', class_='tgme_widget_message_date')
    post_link = link_tag['href'] if link_tag else ''
    post_id_match = re.search(r'/(\d+)$', post_link)
    post_id = post_id_match.group(1) if post_id_match else None

    photo_divs = post_html.find_all('a', class_='tgme_widget_message_photo_wrap')
    photo_urls = [re.search(r"url\('(.*?)'\)", div['style']).group(1) 
                 for div in photo_divs if 'style' in div.attrs]

 # Проверяем наличие видео
    video_div = post_html.find('div', class_='tgme_widget_message_video_wrap')
    has_video = video_div is not None
    
    has_file = post_html.find('div', class_='tgme_widget_message_document') is not None or '📎' in text

    return {
        'id': post_id,
        'text': text,
        'photo_urls': photo_urls,
        'link': post_link,
        'channel': channel,
        'has_file': has_file,
        'has_video': has_video  # Добавляем флаг наличия видео
    }