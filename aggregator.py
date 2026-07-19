import feedparser
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import hashlib

# 50+ топовых RSS источников
RSS_FEEDS = {
    # МЕЖДУНАРОДНЫЕ НОВОСТИ
    "BBC World": {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "Мир", "priority": 1},
    "BBC Business": {"url": "http://feeds.bbci.co.uk/news/business/rss.xml", "category": "Бизнес", "priority": 2},
    "BBC Tech": {"url": "http://feeds.bbci.co.uk/news/technology/rss.xml", "category": "Технологии", "priority": 3},
    "Reuters World": {"url": "https://www.reutersagency.com/feed/?best-for-wordpress=1&post_type=best", "category": "Мир", "priority": 4},
    "Reuters Business": {"url": "https://feeds.reuters.com/reuters/businessNews", "category": "Бизнес", "priority": 5},
    "CNN Top": {"url": "http://rss.cnn.com/rss/edition.rss", "category": "Мир", "priority": 6},
    "Al Jazeera": {"url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "Мир", "priority": 7},
    "The Guardian": {"url": "https://www.theguardian.com/world/rss", "category": "Мир", "priority": 8},
    "NY Times": {"url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "category": "Мир", "priority": 9},
    "Washington Post": {"url": "https://feeds.washingtonpost.com/rss/world", "category": "Мир", "priority": 10},
    
    # ТЕХНОЛОГИИ
    "TechCrunch": {"url": "https://techcrunch.com/feed/", "category": "Технологии", "priority": 11},
    "The Verge": {"url": "https://www.theverge.com/rss/index.xml", "category": "Технологии", "priority": 12},
    "Wired": {"url": "https://www.wired.com/feed/rss", "category": "Технологии", "priority": 13},
    "Ars Technica": {"url": "https://arstechnica.com/feed/", "category": "Технологии", "priority": 14},
    "Engadget": {"url": "https://www.engadget.com/rss.xml", "category": "Технологии", "priority": 15},
    "Mashable": {"url": "https://mashable.com/feed/", "category": "Технологии", "priority": 16},
    "Gizmodo": {"url": "https://gizmodo.com/feed", "category": "Технологии", "priority": 17},
    
    # БИЗНЕС И ФИНАНСЫ
    "Bloomberg": {"url": "https://www.bloomberg.com/feed/podcast/world.xml", "category": "Бизнес", "priority": 18},
    "Forbes": {"url": "https://www.forbes.com/world/feed/", "category": "Бизнес", "priority": 19},
    "Fortune": {"url": "http://fortune.com/feed/", "category": "Бизнес", "priority": 20},
    "CNBC": {"url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "category": "Бизнес", "priority": 21},
    "Financial Times": {"url": "https://www.ft.com/world?format=rss", "category": "Бизнес", "priority": 22},
    "Economist": {"url": "https://www.economist.com/international/rss.xml", "category": "Бизнес", "priority": 23},
    
    # РОССИЙСКИЕ ИСТОЧНИКИ
    "Habr": {"url": "https://habr.com/ru/rss/all/top/", "category": "Технологии", "priority": 24},
    "VC.ru": {"url": "https://vc.ru/feed", "category": "Бизнес", "priority": 25},
    "Lenta.ru": {"url": "https://lenta.ru/rss/news", "category": "Новости", "priority": 26},
    "Meduza": {"url": "https://meduza.io/rss/all", "category": "Общество", "priority": 27},
    "РБК": {"url": "https://www.rbc.ru/rbcnews/rss/", "category": "Новости", "priority": 28},
    "Коммерсантъ": {"url": "https://www.kommersant.ru/RSS/news_day.xml", "category": "Новости", "priority": 29},
    "Ведомости": {"url": "https://www.vedomosti.ru/rss/news.xml", "category": "Бизнес", "priority": 30},
    "TJ": {"url": "https://tjournal.ru/feed", "category": "Технологии", "priority": 31},
    "DTF": {"url": "https://dtf.ru/feed", "category": "Развлечения", "priority": 32},
    "Kanal Telegram": {"url": "https://telegra.ph/rss", "category": "Новости", "priority": 33},
    
    # НАУКА
    "Nature": {"url": "https://www.nature.com/nature.rss", "category": "Наука", "priority": 34},
    "Science Daily": {"url": "https://www.sciencedaily.com/rss/all.xml", "category": "Наука", "priority": 35},
    "New Scientist": {"url": "https://www.newscientist.com/feed/home/", "category": "Наука", "priority": 36},
    "Scientific American": {"url": "https://www.scientificamerican.com/rss/current-issue.xml", "category": "Наука", "priority": 37},
    
    # КУЛЬТУРА И ОБЩЕСТВО
    "NPR": {"url": "https://feeds.npr.org/1001/rss.xml", "category": "Общество", "priority": 38},
    "TIME": {"url": "http://feeds.time.com/time/topstories", "category": "Общество", "priority": 39},
    "Atlantic": {"url": "https://www.theatlantic.com/feed/all/", "category": "Общество", "priority": 40},
    
    # СПОРТ
    "ESPN": {"url": "http://www.espn.com/espn/rss/news", "category": "Спорт", "priority": 41},
    "BBC Sport": {"url": "http://feeds.bbci.co.uk/sport/rss.xml", "category": "Спорт", "priority": 42},
    
    # ЗДОРОВЬЕ
    "Health.com": {"url": "https://www.health.com/rss/all", "category": "Здоровье", "priority": 43},
    "WebMD": {"url": "https://rss.webmd.com/rss/rss.aspx?RSSSource=RSS_Public", "category": "Здоровье", "priority": 44},
    
    # ДОПОЛНИТЕЛЬНЫЕ ТЕХ
    "GitHub Blog": {"url": "https://github.blog/feed/", "category": "Технологии", "priority": 45},
    "Stack Overflow": {"url": "https://stackoverflow.blog/feed/", "category": "Технологии", "priority": 46},
    "Product Hunt": {"url": "https://www.producthunt.com/feed", "category": "Технологии", "priority": 47},
    "Indie Hackers": {"url": "https://www.indiehackers.org/feed", "category": "Бизнес", "priority": 48},
    "Y Combinator": {"url": "https://news.ycombinator.com/rss", "category": "Технологии", "priority": 49},
    "Dev.to": {"url": "https://dev.to/feed", "category": "Технологии", "priority": 50},
    "Medium Top": {"url": "https://medium.com/feed/tag/technology", "category": "Технологии", "priority": 51},
    "Fast Company": {"url": "https://www.fastcompany.com/rss", "category": "Бизнес", "priority": 52},
}

def extract_image_from_entry(entry, feed_url):
    """Извлекает изображение из RSS"""
    image_url = None
    
    # 1. media:content
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if media.get('medium') == 'image' or media.get('type', '').startswith('image'):
                image_url = media.get('url')
                break
    
    # 2. media:thumbnail
    if not image_url and hasattr(entry, 'media_thumbnail'):
        image_url = entry.media_thumbnail[0].get('url')
    
    # 3. Ищем в content/summary
    if not image_url:
        content = entry.get('summary', '') + entry.get('description', '')
        img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
        if img_match:
            image_url = img_match.group(1)
    
    # 4. enclosure
    if not image_url and hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            if enclosure.type.startswith('image'):
                image_url = enclosure.href
                break
    
    # 5. Парсим страницу для Habr и VC
    if not image_url and any(x in feed_url for x in ['habr.com', 'vc.ru', 'tjournal.ru']):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            page = requests.get(entry.link, headers=headers, timeout=5)
            soup = BeautifulSoup(page.content, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image_url = og_image.get('content')
        except:
            pass
    
    # 6. Заглушка
    if not image_url:
        categories = {
            "Технологии": "technology",
            "Бизнес": "business",
            "Мир": "world",
            "Новости": "news",
            "Общество": "society",
            "Наука": "science",
            "Спорт": "sport",
            "Здоровье": "health",
            "Развлечения": "entertainment"
        }
        category = "news"
        for src_name, src_info in RSS_FEEDS.items():
            if src_info['url'] == feed_url:
                category = src_info.get('category', 'news').lower()
                break
        keyword = categories.get(category, 'news')
        image_url = f"https://source.unsplash.com/800x600/?{keyword},news"
    
    return image_url

def get_news_hash(title, excerpt):
    """Создаёт хэш новости для дедупликации"""
    text = (title + excerpt).lower().strip()
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def fetch_news():
    """Собирает новости с дедупликацией"""
    all_news = []
    seen_hashes = set()
    
    print(f"\n🚀 Начинаю сбор новостей: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📰 Источников: {len(RSS_FEEDS)}\n")
    
    for source_name, source_info in RSS_FEEDS.items():
        try:
            print(f"  → {source_name}...")
            feed = feedparser.parse(source_info['url'])
            
            # Берём топ-1 от каждого источника (чтобы не было дублей)
            for entry in feed.entries[:1]:
                # Проверяем на дубликаты
                summary = entry.get('summary', entry.get('description', ''))
                clean_summary = re.sub(r'<[^>]+>', '', summary)[:150].strip()
                news_hash = get_news_hash(entry.title, clean_summary)
                
                if news_hash in seen_hashes:
                    print(f"    ⏭️  Дубль, пропускаем")
                    continue
                
                seen_hashes.add(news_hash)
                
                # Извлекаем данные
                image_url = extract_image_from_entry(entry, source_info['url'])
                
                news_item = {
                    "category": source_info['category'],
                    "title": entry.title,
                    "excerpt": clean_summary + "..." if len(clean_summary) > 0 else "Без описания",
                    "image": image_url,
                    "source": source_name,
                    "link": entry.get('link', '#'),
                    "published": entry.get('published', ''),
                    "time": datetime.now().strftime("%H:%M"),
                    "hash": news_hash
                }
                
                all_news.append(news_item)
                print(f"    ✓ {entry.title[:60]}...")
                
        except Exception as e:
            print(f"    ✗ Ошибка: {str(e)[:50]}")
    
    # Сортируем по приоритету
    all_news.sort(key=lambda x: RSS_FEEDS.get(x['source'], {}).get('priority', 99))
    
    # Берём топ-12 уникальных новостей
    final_news = all_news[:12]
    
    # Сохраняем
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump({
            "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "total": len(final_news),
            "sources_count": len(RSS_FEEDS),
            "next_update": (datetime.now() + timedelta(minutes=5)).strftime("%H:%M"),
            "news": final_news
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Готово!")
    print(f"📊 Собрано: {len(final_news)} уникальных новостей")
    print(f"🔄 Следующее обновление: {(datetime.now() + timedelta(minutes=5)).strftime('%H:%M')}")
    print(f"📁 Сохранено в news.json\n")

if __name__ == "__main__":
    fetch_news()
