import fake_headers
import requests
from bs4 import BeautifulSoup
from scrapper import Scraper


if __name__ == '__main__':
    def get_page_count(search_word: str):
        params = {'text': search_word, 'area': [1, 2], 'items_on_page': 20}
        headers = fake_headers.Headers(headers=True).generate()
        response = requests.get('https://spb.hh.ru/search/vacancy', params=params, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        total_pages = soup.find_all('a', {'data-qa': 'pager-page'})

        return total_pages[-1].text


    while True:
        search_word = input('Введите слово для поиска: ')
        keyword_plus = input('Введите дополнительные слова для поиска(через пробел): ').split(' ')
        page_count = int(input(f'Введите кол-во страниц для поиска(доступно {get_page_count(search_word)}): '))

        currency_dict = {
            '1': ('$', 'USD'),
            '2': ('₽', 'RUB'),
            '3': ('€', 'EUR'),
        }
        for key, value in currency_dict.items():
            print(f'{key} - {value[0]} ({value[1]})')
        currency = input('Выберите валюту: ')

        if currency not in currency_dict:
            print('Такой валюты нет')
            continue
        else:
            currency = currency_dict[currency][0]

        print('Программа запущена')
        scraper = Scraper(search_word, keyword_plus, currency, page_count)
        scraper.get_vacancies()

        print('Программа завершена')
        break
