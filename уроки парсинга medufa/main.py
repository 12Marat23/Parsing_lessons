import csv
import requests
from bs4 import BeautifulSoup
import json

url = 'https://medufa.ru/spets/'
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36"
}
if not 'index.html':
    req = requests.get(url, headers=headers)
    src = req.text
    with open('index.html', 'w', encoding="utf-8") as file:
        file.write(src)


with open('index.html', encoding='utf-8') as file:
    src = file.read()
soup = BeautifulSoup(src, 'lxml')
data = []
for item in soup.find_all('div', class_='spec-list-item'):
    a_tags = 'https://medufa.ru/' + item.find('a', class_='spec-list-link').get('href')
    h2_tag = item.find('h2')
    name = h2_tag.get_text(' ', strip=True)
    p_tag = item.find('p')
    row = {'Name': name, 'Link': a_tags, 'position': p_tag.text}
    data.append(row)

with open(f'data/medufa.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

with open(f'data/medufa.json', 'w', encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
