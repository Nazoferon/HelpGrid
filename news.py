from bs4 import BeautifulSoup
import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import json






def search_news():
    url = "http://ttinv.org.ua/category/news/"
    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 109.0.0.0Safari / 537.36OPR / 95.0.0.0"
    }
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    news_dict = {}
    all_links = soup.find_all('section', class_="content")
    for link in all_links:
        news_title = link.find("h2", class_="post-title").text.strip()
        news_img = link.find("img").get('src')
        news_date = link.find("div", class_="post-date").text.strip()
        news_content = link.find("div", class_="post-content").text.strip()
        news_link = link.find("a").get('href')
        news_id = link.find("a").get('href').split("/")[4]
        ikeyboard_news = InlineKeyboardMarkup()
        ik_news = InlineKeyboardButton(text=(f"Посилання: {news_title}"), url=news_link)
        ikeyboard_news.add(ik_news)
        news_dict[news_id] = {
            "news_title": news_title,
            "news_img": news_img,
            "news_date": news_date,
            "news_content": news_content,
            "news_link": news_link
        }

    with open("news_dict.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)





def check_news_update_json():
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    url = "http://ttinv.org.ua/category/news/"
    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 109.0.0.0Safari / 537.36OPR / 95.0.0.0"
    }
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    all_links = soup.find_all('section', class_="content")


    fresh_news = {}
    for links in all_links:
        news_id = links.find("a").get('href').split("/")[4]

        if news_id in news_dict:
            print("ID новин вже є у списку")
            continue
        else:
            print("Новин з таким ID немає. Добавимо!")
            news_title = links.find("h2", class_="post-title").text.strip()
            news_date = links.find("div", class_="post-date").text.strip()
            news_content = links.find("div", class_="post-content").text.strip()
            global news_img
            news_img = links.find("img").get('src')
            news_link = links.find("a").get('href')
            news_id = links.find("a").get('href').split("/")[4]

            news_dict[news_id] = {
                "news_title": news_title,
                "news_img": news_img,
                "news_date": news_date,
                "news_content": news_content,
                "news_link": news_link
            }

            fresh_news[news_id] = {
                "news_title": news_title,
                "news_img": news_img,
                "news_date": news_date,
                "news_content": news_content,
                "news_link": news_link
            }

    with open("news_dict.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)
        
    return fresh_news

def main():
    search_news()
    check_news_update_json()



if __name__ == '__main__':
    main()