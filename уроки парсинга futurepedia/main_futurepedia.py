import csv
import json
import os
import sqlite3
from typing import List
from urllib.parse import urlparse
import requests
import time
import random
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict


@dataclass
class AI:
    name: str
    description: str
    link: str

    def to_dict(self):
        return asdict(self)


cookies = {
    '_ga': 'GA1.1.692771350.1718611961',
    'cookie_consent': 'true',
    'cf_clearance': '.sAxPY48HHDCXkHfZ.1fxqhwkogpBgF_YtPWXOCMYKA-1718886275-1.0.1.1-JNGlGqFNR6LmmNd99ePUGp9dmJXY9RU1TVjDmIUfRbUk0X.A0hIbt5duGHO7E2ES_mOGwPRC9cf_wGyTR0R9kw',
    '_ga_HQ45GJVJVY': 'GS1.1.1718886272.8.1.1718887546.0.0.0',
}

headers = {
    'authority': 'www.futurepedia.io',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9,tt;q=0.8,es;q=0.7,ko;q=0.6,la;q=0.5',
    # 'cookie': '_ga=GA1.1.692771350.1718611961; cookie_consent=true; cf_clearance=.sAxPY48HHDCXkHfZ.1fxqhwkogpBgF_YtPWXOCMYKA-1718886275-1.0.1.1-JNGlGqFNR6LmmNd99ePUGp9dmJXY9RU1TVjDmIUfRbUk0X.A0hIbt5duGHO7E2ES_mOGwPRC9cf_wGyTR0R9kw; _ga_HQ45GJVJVY=GS1.1.1718886272.8.1.1718887546.0.0.0',
    'referer': 'https://www.futurepedia.io/ai-tools/3D-generator',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36',
}


def make_request(url: str, page: str):
    """
    Этот метод получает ссылку на страницу и формирует Get-запрос
     Если полученная ссылка является корректной, то проверяет наличие
      на странице элемента 'div' с классом "flex flex-col items-start".
      Если такой элемент существует, функция возвращает текст ответа,
      в противном случае возвращает None.
      Если возникает ошибка при выполнении запроса,
      функция выводит сообщение об ошибке и возвращает None.
    """
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        print(f'{page} - {response.status_code}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            if soup.find('div', class_="flex flex-col items-start"):
                return response.text
            else:
                None
        else:
            return None
    except requests.RequestException as e:
        print(f'Ошибка запроса: {e}')
        return None


def start(base_url: str):
    """Стартовая функция. Получает ссылку на главную страницу
    и формирует запросы на следующие страницы, где находятся
    искомые данные. В случае получения корректных данных запускает
    функцию parser()
    """
    create_csv()
    page = 1
    status = True
    while status:
        if page == 1:
            current_url = f'https://www.futurepedia.io/ai-tools/3D-generator'
        else:
            current_url = f'{base_url}?page={page}'
        src = make_request(current_url, page)
        if src:
            page += 1
            time.sleep(random.randint(1, 3))
            parser(src)
        else:
            status = False


def parser(page: str):
    """ Поиск искомых данных в полученной странице. Так же
    формирует запрос на проверку полный ли путь в функции is_absolute_url() получает переменная
     если нет то, запускает функцию search_url()
    """
    list_ai = []
    soup = BeautifulSoup(page, 'lxml')
    generators = soup.find_all('div',
                               class_="flex flex-col bg-card text-card-foreground xl:aspect-square h-full w-full rounded-xl border shadow-lg")
    for generator in generators:
        name = generator.find(class_="m-0 line-clamp-2 overflow-hidden text-xl font-semibold text-slate-700").text
        description = generator.find(
            class_="text-muted-foreground my-2 line-clamp-2 overflow-hidden overflow-ellipsis px-6 text-base").text
        link = "https://www.futurepedia.io" + generator.find(
            class_="px-6 pb-2 pt-4 flex h-24 flex-row items-start gap-4").find('a').get('href')
        link_ai = generator.find(class_="hover:no-underline").get('href')
        if not is_absolute_url(link_ai):
            link_ai = search_url(link)
        list_ai.append(AI(
            name=name,
            description=description,
            link=link_ai
        ))
    create_bd(list_ai)
    write_csv(list_ai)
    write_json(list_ai)


def is_absolute_url(url: str):
    # Проверяем, начинается ли URL с 'http' или 'https'
    return bool(urlparse(url).scheme)


def search_url(url: str):
    # Заходим на страницу с описанием и берем ссылку на официальную страницу
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            link = soup.find('a', class_="hover:no-underline").get('href')
            return link
    except requests.RequestException as e:
        print(f'Ошибка запроса: {e}')
        return None


def create_bd(ai_db: list[AI]):
    conn = sqlite3.connect('data/ai_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS  list_ai(
              name TEXT,
              description TEXT,
              link TEXT
             )''')
    for item in ai_db:
        c.execute('INSERT INTO list_ai (name, description, link) VALUES (?, ?, ?)',
                  (item.name, item.description, item.link))
    conn.commit()
    conn.close()


def create_csv():
    with open('data/ai_db.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'name',
            'description',
            'link',
        ])


def write_csv(ai_csv: list[AI]):
    with open('data/ai_db.csv', 'a+', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in ai_csv:
            writer.writerow([
                item.name,
                item.description,
                item.link
            ])


def write_json(ai_list: List[AI], file_path='data/ai_json.json'):
    # Проверяем, существует ли файл
    if os.path.exists(file_path):
        # Читаем существующие данные
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Добавляем новые данные
    ai_dicts = [ai.to_dict() for ai in ai_list]
    existing_data.extend(ai_dicts)

    # Перезаписываем файл с обновленными данными
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file,  indent=4,  ensure_ascii=False)


if __name__ == '__main__':
    start('https://www.futurepedia.io/ai-tools/3D-generator')
