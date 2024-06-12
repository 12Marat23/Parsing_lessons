import os.path
import requests
from bs4 import BeautifulSoup
import csv
from model import Product


def save_file(base_url: str):
    create_csv()
    for i in range(1, 12):
        url = f"{base_url}?limit=100&p={i}"
        if not os.path.isfile(f'data/index_{i}.html'):
            res = requests.get(url=url)
            src = res.text
            with open(f'data/index_{i}.html', 'w', encoding="utf-8") as file:
                file.write(src)
        parser(i)


def parser(page_num: int):
    count = 0
    list_product = []
    with open(f'data/index_{page_num}.html', encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    products = soup.find_all("div", class_="product-card")
    for product in products:
        name = product.get("data-product-name")
        sku = product.find("span", class_="product-card__key").text
        name_element = product.find("meta", itemprop="name")
        link = name_element.findNext().get('href')
        try:
            price = product.find('span', itemprop="price").get("content")
        except:
            price = 0
        count += 1
        list_product.append(Product(count=count,
                                    sku=sku,
                                    name=name,
                                    link=link,
                                    price=price))
    write_csv(list_product, page_num)


def create_csv():
    with open(f"data/glavsnab.csv", "w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'count',
            'sku',
            'name',
            'link',
            'price', ])


def write_csv(products: list[Product], page_num: int):
    with open(f"data/glavsnab.csv", "a+", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        for product in products:
            writer.writerow([
                product.count+100*(page_num-1),
                product.sku,
                product.name,
                product.link,
                product.price
            ])


if __name__ == '__main__':
    save_file("https://glavsnab.net/santehnika/rakoviny-i-komplektuyushchiye/rakoviny.html")
