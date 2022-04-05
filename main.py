import os
import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime

current_time = datetime.now().strftime("%d_%m_%Y")


def get_html(url):
    headers = {
        'user-agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Mobile Safari/537.36'
    }
    res = requests.get(url=url, headers=headers).text
    return res


def make_page(pages_name, html):
    if not os.path.exists('pages'):
        os.mkdir('pages')

    with open(f'pages/{pages_name}.html', 'a', encoding='utf8') as file:
        file.write(html)


def get_pages_count(url):
    html = get_html(url)
    make_page('main_page', html)

    with open('pages/main_page.html', encoding='utf8') as file:
        page = file.read()
        soup = BeautifulSoup(page, 'lxml')
        pages_count = len(
            soup.find('div', class_='bx-pagination-container').find(
                'ul').find_all('li')) - 1
    return pages_count


def make_json(data):
    with open(f'{current_time}.json', 'a') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def write_csv(data):
    with open(f'{current_time}.csv', 'a', encoding='utf-8-sig') as file:
        order = ['articul', 'url', 'price']
        writer = csv.DictWriter(file, fieldnames=order)
        writer.writerow(data)


def main():
    url = 'https://shop.casio.ru/catalog/filter/gender-is-male/apply/'
    pages_count = get_pages_count(url)
    headers = {
        'articul': 'Артикул',
        'url': 'Адрес товара',
        'price': 'Цена руб.'
    }
    write_csv(headers)
    json_data = []
    for i in range(1, pages_count + 1):
        url = f'https://shop.casio.ru/catalog/filter/gender-is-male/apply/?PAGEN_1={i}'
        make_page(f'page_{i}', get_html(url))

        with open(f'pages/page_{i}.html', encoding='utf8') as file:
            html = file.read()
            soup = BeautifulSoup(html, 'lxml')
            product_cards = soup.find_all('div', class_='product-item')
            for product in product_cards:
                try:
                    product_articul = product.find(
                        'p', class_='product-item__articul').text.strip()
                    product_url = 'https://shop.casio.ru/' + product.find(
                        'a', class_='product-item__link').get('href').strip()
                    product_price = int(
                        product.get('data-analitics').split("'price':")
                        [1].split(',')[0])

                    data = {
                        'articul': product_articul,
                        'url': product_url,
                        'price': product_price
                    }
                    json_data.append(data)
                    write_csv(data)

                except:
                    print('Error')

    make_json(json_data)


if __name__ == '__main__':
    main()