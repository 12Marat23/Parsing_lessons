import csv
import sqlite3
import requests
import time
import random
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Products:
    product_card: str
    selector: str
    link: str




headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru,en;q=0.9,tt;q=0.8,es;q=0.7,ko;q=0.6,la;q=0.5',
    'Connection': 'keep-alive',
    # 'Cookie': '_ga=GA1.1.1498591729.1718631520; csrftoken=FQ18ARtCVdahYOY36NJrbpZbpfFFVuqvHHVWTf0quFK6nHGs3xCcEdRvOi4BrNfo; _ga_FY4MED6WW4=GS1.1.1718710364.2.1.1718710940.0.0.0',
    'Referer': 'https://parsemachine.com/sandbox/catalog/tovar-1/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def create_csv():
    with open('data/products.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'product_card',
            'selector',
            'link',
        ])


def write_csv(products: list[Products]):
    with open('data/products.csv', 'a+', encoding='utf-8') as file:
        writer = csv.writer(file)
        for product in products:
            writer.writerow([
                product.product_card,
                product.selector,
                product.link
            ])


def save_file(base_url: str):
    create_csv()
    status = True
    page = 1
    while status:
        response = requests.get(url=f'{base_url}?page={page}', headers=headers)
        if response.status_code == 200:
            src = response.text
            page += 1
            time.sleep(random.randint(1, 3))
            parser(src)
        else:
            status = False


def parser(page: str):
    list_products = []
    src = BeautifulSoup(page, 'lxml')
    products = src.find_all('div', class_="col-6 col-md-4 col-xl-3 mb-3")
    for product in products:
        link = 'https://parsemachine.com/sandbox' + product.find(class_="no-hover title").get('href')
        product_card = product.find(class_="no-hover title").text.strip()
        selector = product.find('p', class_="mb-1").text.strip()
        list_products.append(Products(
            product_card=product_card,
            selector=selector,
            link=link
        ))
    write_csv(list_products)
    create_bd(list_products)


def create_bd(products: list[Products]):
    conn = sqlite3.connect('data/products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS  products_list(
              product_card TEXT,
              selector TEXT,
              link TEXT
             )''')
    for product in products:
        c.execute('INSERT INTO products_list (product_card, selector, link) VALUES (?, ?, ?)',
                  (product.product_card, product.selector, product.link))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    save_file('https://parsemachine.com/sandbox/catalog/')
