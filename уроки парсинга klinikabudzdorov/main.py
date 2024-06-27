import requests
import os
from bs4 import BeautifulSoup
import csv
from model import Doctors

headers = {
    'authority': 'kazan.klinikabudzdorov.ru',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru,en;q=0.9,tt;q=0.8,es;q=0.7,ko;q=0.6,la;q=0.5',
    'cache-control': 'max-age=0',
    # 'cookie': '__ddg1_=FNtLcRaIWUiIJWXE8gXu; mindboxDeviceUUID=096df676-5d1c-4fe7-a259-c1f54e15870f; directCrm-session=%7B%22deviceGuid%22%3A%22096df676-5d1c-4fe7-a259-c1f54e15870f%22%7D; _ct=800000000865693178; _ct_client_global_id=3db48937-034e-5f91-92e9-617cf4a702e2; _ym_uid=1717672830715499486; _ym_d=1717672830; _gid=GA1.2.2121566541.1718255588; REGIONALITY_REGION_ID=7; REGIONALITY_REGION_CURRENT=Y; session=1; cted=modId%3De7elek0q%3Bclient_id%3D653297622.1717672823%3Bya_client_id%3D1717672830715499486; _ct_ids=e7elek0q%3A26746%3A2000587728; _ct_session_id=2000587728; _ct_site_id=26746; _ym_visorc=b; _ym_isad=2; _ga_PGZWSNBNFY=GS1.1.1718347651.7.1.1718348710.0.0.0; _ga=GA1.2.653297622.1717672823; call_s=%3C!%3E%7B%22e7elek0q%22%3A%5B1718350512%2C2000587728%2C%7B%22114600%22%3A%22360077%22%7D%5D%2C%22d%22%3A3%7D%3C!%3E; PHPSESSID=nr0opXI7OMw7voc0V1sbrYsijB5PfiIv',
    'if-modified-since': 'Fri, 14 Jun 2024 05:58:14 GMT',
    'if-none-match': '028c3fef3feb786ab508d2eb4a081636',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36',
}


def save_file(base_url: str):
    create_csv()
    count = 0
    for num in range(1, 11):
        url = f"{base_url}page-{num}/"
        if not os.path.isfile(f'index/index_{num}.html'):
            reg = requests.get(url, headers=headers)
            src = reg.text
            with open(f'index/index_{num}.html', 'w', encoding="utf-8") as file:
                file.write(src)
        count = parser(num, count)


def parser(page_num: int, count: int):
    list_doc = []
    with open(f'index/index_{page_num}.html', encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    doctors = soup.find_all('div', class_="b-doctors-list__item")
    for doctor in doctors:
        name = doctor.find(class_="e-doctor-card-2__name").text
        profession = doctor.find(class_="e-doctor-card-2__spec").text
        link_element = doctor.find('a', class_="e-doctor-card-2__image")
        if link_element:
            link = link_element.get('href')
        link = f'https://kazan.klinikabudzdorov.ru{link}'
        try:
            experience = doctor.find(class_="e-doctor-card-2__exp").text
        except:
            experience = '0'
        count += 1
        list_doc.append(Doctors(
            count=count,
            name=name,
            profession=profession,
            experience=experience.strip(),
            link=link
        ))
        print(f"{count}. {name}, {profession} , {experience.strip()}, {link}")
    write_csv(list_doc)
    return count


def create_csv():
    with open('data/doctors.csv', 'w', newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Номер',
            'ФИО',
            'Специальность',
            'Стаж',
            'Ссылка'
        ])


def write_csv(doctors: list[Doctors]):
    with open('data/doctors.csv', 'a+', newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        for doctor in doctors:
            writer.writerow([
                doctor.count,
                doctor.name,
                doctor.profession,
                doctor.experience
            ])


if __name__ == '__main__':
    save_file('https://kazan.klinikabudzdorov.ru/vrachi/')
