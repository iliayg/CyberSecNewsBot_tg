import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup


token ="add your bot token here" 
method = '{method}'
BOT_URL = f"https://api.telegram.org/bot{token}/{method}"
OFFSET = 0
fresh_news = {}


def new_user():
    tg_request = requests.get(BOT_URL.format(method=f"getUpdates?offset={OFFSET}"))
    info = json.loads(tg_request.text)
    result = info['result']
    for entry in result:
        message_id = entry['message']['message_id']
        update_id = entry['update_id']
        new_user_id = entry['message']['from']['id']
        first_name = entry['message']['from']['first_name']
        username = entry['message']['from']['username']
        date = entry['message']['date']

        user_id = []
        with open('users_dict.json') as file:
            users = json.load(file)

        for k in users:
            user_id.append(k['user_id'])
        if new_user_id in user_id:
            break
        else:
            users_dict = {
                "user_id": new_user_id,
                "update_id": update_id,
                "message_id": message_id,
                "first_name": first_name,
                "username": username,
                "date": date
            }
        users.append(users_dict)
        with open('users_dict.json', 'w') as file:
            json.dump(users, file, indent=4, ensure_ascii=False)


def get_first_news():
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.3538.77 Safari/537.36"
    }
    url = "https://www.securitylab.ru/news"
    req = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(req.text, "lxml")
    article_cards = soup.find_all("a", class_="article-card")

    for article in article_cards:
        article_title = article.find("h2", class_="article-card-title").text.strip()
        article_desc = article.find("p").text.strip()
        article_url = f'https://www.securitylab.ru{article.get("href")}'

        article_date_time = article.find("time").get("datetime")
        date_from_iso = datetime.fromisoformat(article_date_time)
        date_time = datetime.strftime(date_from_iso, "%Y-%m-%d %H:%M:%S")
        article_date_timestamp = time.mktime(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple())

        article_id = article_url.split("/")[-1]
        article_id = article_id[:-4]

        fresh_news[article_id] = {
            "article_date_timestamp": article_date_timestamp,
            "article_title": article_title,
            "article_url": article_url,
            "article_desc": article_desc
        }
    return fresh_news


def save_in_json():
    with open("news_dict.json", "w") as file:
        json.dump(fresh_news, file, indent=4, ensure_ascii=False)


def check_news_update():
    article_id = []
    with open("news_dict.json", "r") as file:
        news_dict = json.load(file)
        for k, v in news_dict.items():
            article_id.append(k)

    updated_news = []
    fresh_news = get_first_news()
    for k, v in fresh_news.items():
        if k not in article_id:
            for each in fresh_news.items():
                for i in each:
                    if k == i:
                        updated_news.append(each)
    return updated_news


def main():
    get_first_news()
