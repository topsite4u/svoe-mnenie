import feedparser
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Источники RSS с приоритетами
RSS_FEEDS = {
    "BBC": {
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "Мир",
        "priority": 1
    },
    "Reuters": {
        "url": "https://www.reutersagency.com/feed/?best-for-wordpress=1&post_type=best",
        "category": "Бизнес",
        "priority": 2
    },
    "Habr": {
        "url": "https://habr.com/ru/rss/all/top/",
        "category": "Технологии",
        "priority": 3
    },
    "VC.ru": {
        "url": "https://vc.ru/feed",
        "category": "Бизнес",
        "priority": 4
    },
    "Lenta.ru": {
        "url": "https://lenta.ru/rss/news",
        "category": "Новости",
        "priority": 5
    },
    "Meduza": {
        "url": "https://meduza.io/rss/all",
        "category": "Общество",
        "priority": 6
    }
}

def extract_image_from_entry(entry, feed_url):
    """Извлекает изображение из RSS записи"""
    image_url = None
    
    # 1. Пробуем media:content (стандарт RSS)
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if media.get('medium') == 'image' or media.get('type', '').startswith('image'):
                image_url = media.get('url')
                break
    
    # 2. Пробуем media:thumbnail
    if not image_url and hasattr(entry, 'media_thumbnail'):
        image_url = entry.media_thumbnail[0].get('url')
    
    # 3. Ищем в content/summary
    if not image_url:
        content = entry.get('summary', '') + entry.get('description', '')
        # Ищем теги img
        img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
        if img_match:
            image_url = img_match.group(1)
    
    # 4. Ищем enclosure
    if not image_url and hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            if enclosure.type.startswith('image'):
                image_url = enclosure.href
                break
    
    # 5. Для Habr и VC пробуем парсить страницу
    if not image_url and 'habr.com' in feed_url:
        try:
            page = requests.get(entry.link, timeout=5)
            soup = BeautifulSoup(page.content, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image_url = og_image.get('content')
        except:
            pass
    
    if not image_url and 'vc.ru' in feed_url:
        try:
            page = requests.get(entry.link, timeout=5)
            soup = BeautifulSoup(page.content, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image_url = og_image.get('content')
        except:
            pass
    
    # 6. Заглушка если ничего не нашли
    if not image_url:
        # Выбираем случайную тематическую картинку с Unsplash
        categories = {
            "Технологии": "technology",
            "Бизнес": "business",
            "Мир": "world",
            "Новости": "news",
            "Общество": "society"
        }
        category = RSS_FEEDS.get([k for k, v in RSS_FEEDS.items() if v['url'] == feed_url][0], {}).get('category', 'news')
        keyword = categories.get(category, 'news')
        image_url = f"https://source.unsplash.com/800x600/?{keyword},news"
    
    return image_url

def fetch_news():
    """Собирает новости из всех источников"""
    all_news = []
    
    print(f" Начинаю сбор новостей: {datetime.now().strftime('%H:%M:%S')}")
    
    for source_name, source_info in RSS_FEEDS.items():
        try:
            print(f"  → Загружаю {source_name}...")
            feed = feedparser.parse(source_info['url'])
            
            # Берём топ-2 новости от каждого источника
            for entry in feed.entries[:2]:
                # Извлекаем картинку
                image_url = extract_image_from_entry(entry, source_info['url'])
                
                # Форматируем описание (убираем HTML теги)
                summary = entry.get('summary', '')
                if not summary:
                    summary = entry.get('description', '')
                # Удаляем HTML теги
                clean_summary = re.sub(r'<[^>]+>', '', summary)
                # Оставляем первые 150 символов
                clean_summary = clean_summary[:150].strip() + "..."
                
                news_item = {
                    "category": source_info['category'],
                    "title": entry.title,
                    "excerpt": clean_summary,
                    "image": image_url,
                    "source": source_name,
                    "link": entry.get('link', '#'),
                    "published": entry.get('published', ''),
                    "time": datetime.now().strftime("Сегодня, %H:%M")
                }
                
                all_news.append(news_item)
                print(f"    ✓ Добавлено: {entry.title[:50]}...")
                
        except Exception as e:
            print(f"  ✗ Ошибка {source_name}: {str(e)}")
    
    # Сортируем по приоритету источника
    all_news.sort(key=lambda x: RSS_FEEDS.get(x['source'], {}).get('priority', 99))
    
    # Сохраняем в JSON
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump({
            "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "total": len(all_news),
            "news": all_news
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Готово! Собрано {len(all_news)} новостей")
    print(f"📁 Сохранено в news.json")

if __name__ == "__main__":
    fetch_news()
