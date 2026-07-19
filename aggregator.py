import feedparser
import json
from datetime import datetime
import urllib.request

# Источники RSS (можно добавить любые)
RSS_FEEDS = [
    "https://www.rbc.ru/rbcnews/rss/",
    "https://meduza.io/rss/all",
    "http://feeds.bbci.co.uk/news/world/rss.xml"
]

def fetch_news():
    all_news = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]: # Берем топ-3 из каждого источника
                all_news.append({
                    "category": "Новости",
                    "title": entry.title,
                    "excerpt": entry.get('summary', 'Без описания')[:150] + "...",
                    "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800", # Заглушка, можно парсить реальную картинку
                    "source": feed.feed.get('title', 'Неизвестный источник'),
                    "time": datetime.now().strftime("Сегодня, %H:%M")
                })
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")

    # Сохраняем в файл, который читает фронтенд
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print("Новости успешно обновлены!")

if __name__ == "__main__":
    fetch_news()
