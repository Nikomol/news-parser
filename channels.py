#Логика инициализации и мониторинга каналов
import time
from parser import parse_channel_page, extract_post_data
from telegram_sender import send_to_telegram
from config import channels, KEYWORDS
from filters import is_post_relevant 

last_post_ids = {}

def initialize_channels():
    print("⏳ Инициализация...")
    for ch in channels:
        try:
            post_html = parse_channel_page(ch)
            if not post_html:
                print(f"⚠️ Не удалось получить контент из @{ch}")
                continue
                
            post = extract_post_data(post_html, ch)
            if post:
                last_post_ids[ch] = post['id']
                print(f"🔒 @{ch}: последний пост ID {post['id']}")
            else:
                print(f"⚠️ Не удалось извлечь данные из @{ch}")
                
        except Exception as e:
            print(f"❌ Критическая ошибка в @{ch}: {str(e)}")
            last_post_ids[ch] = None

def monitor_channels():
    print("🚀 Мониторинг каналов...")
    while True:
        for ch in channels:
            try:
                post_html = parse_channel_page(ch)
                if not post_html:
                    continue

                post = extract_post_data(post_html, ch)
                if post['id'] != last_post_ids.get(ch):
                    #if is_post_relevant(post['text'], KEYWORDS):  # 🔍 фильтрация здесь
                    if(post['text']):
                        print(f"📨 @{ch}: новый релевантный пост ID {post['id']}")
                        send_to_telegram(post)
                    else:
                        print(f"⛔ @{ch}: пост ID {post['id']} не прошёл фильтр")
                    last_post_ids[ch] = post['id']
            except Exception as e:
                print(f"❌ Ошибка при обработке @{ch}: {e}")
        time.sleep(1)