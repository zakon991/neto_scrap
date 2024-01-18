import json
import fake_headers
import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, search_word: str, keywords_plus: list, currency: str, page_count: int):
        self.headers = fake_headers.Headers(headers=True).generate()
        self.search_word = search_word
        self.keywords_plus = keywords_plus
        self.currency = currency
        self.page_count = page_count

    def get_vacancies(self):
        self.vacancies = []
        for i in range(self.page_count):
            self.params = {'text': self.search_word, 'area': [1, 2], 'items_on_page': 20, 'page': i}
            self.url = 'https://spb.hh.ru/search/vacancy'
            self.page = requests.get(self.url, params=self.params, headers=self.headers)
            self.soup = BeautifulSoup(self.page.text, "lxml")

            finded_vacancies = self.soup.find_all('div', {'class': 'serp-item'})

            for vacancie in finded_vacancies:
                salary_span = vacancie.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                salary = salary_span.text if salary_span and self.currency in salary_span.text else 'Не указана'

                if self.currency in salary:
                    link = vacancie.find('a').get('href')
                    check_keywords = requests.get(link, headers=self.headers)
                    print(f'Проверка вакансии {link}')
                    check_soup = BeautifulSoup(check_keywords.text, 'lxml')
                    check = check_soup.find('div', {'data-qa': 'vacancy-description'}).text

                    for key in self.keywords_plus:
                        if key.lower() in check.lower():
                            title = vacancie.find('span', {'class': 'serp-item__title'}).text
                            company = vacancie.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text
                            adress = vacancie.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text
                            self.vacancies.append({
                                'link': link,
                                'title': title.replace('\xa0', ' ').strip(),
                                'company': company.replace('\xa0', ' ').strip(),
                                'salary': salary.replace('\u202f', '').strip(),
                                'city': adress.replace('\xa0', ' ').strip()
                            })
            print(f'Страница {i + 1} из {self.page_count}')
            if len(self.vacancies) != 0:
                print(
                    f'Найден{"а" if len(self.vacancies) == 1 else "о"} {len(self.vacancies)} '
                    f'ваканси{"я" if len(self.vacancies) == 1 else "й"}')

            json_filename = 'vacancies.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(self.vacancies, json_file, ensure_ascii=False, indent=4)

