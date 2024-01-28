import json
import tkinter as tk
import webbrowser
from tkinter import ttk
import fake_headers
import requests
from bs4 import BeautifulSoup
from scrapper import Scraper
import threading
from logger import logger

class Inter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("750x500")
        self.setup_gui()

        self.root.mainloop()

    def get_page_count(self, search_word: str):
        params = {'text': search_word, 'area': [1, 2], 'items_on_page': 20}
        headers = fake_headers.Headers(headers=True).generate()
        response = requests.get('https://spb.hh.ru/search/vacancy', params=params, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        total_pages = soup.find_all('a', {'data-qa': 'pager-page'})
        self.root.after(0, lambda: self.update_page_count(total_pages))

    def update_page_count(self, total_pages):
        self.labels[3].configure(text=f'Страницы для поиска: {total_pages[-1].text}')
        self.pages_combobox['values'] = list(range(1, int(total_pages[-1].text) + 1))
        print(self.pages_combobox['values'])

    def on_key_release(self, event):
        if hasattr(self, '_after_id'):
            self.root.after_cancel(self._after_id)

        self._after_id = self.root.after(500, self.start_search_thread)

    def start_search_thread(self):
        threading.Thread(target=self.get_page_count, args=(self.search_word_entry.get(),)).start()

    def setup_gui(self):

        label_texts = ["Слово для поиска", "Доп. ключевые слова", "Валюта", "Страницы для поиска"]
        self.labels = []
        for i, text in enumerate(label_texts):
            label = tk.Label(self.root, text=text)
            label.grid(row=i * 2, column=0)
            self.labels.append(label)

        self.search_word_entry = tk.Entry(self.root)
        self.search_word_entry.grid(row=1, column=0)
        self.search_word_entry.bind('<KeyRelease>', self.on_key_release)

        self.extra_words_entry = tk.Entry(self.root)
        self.extra_words_entry.grid(row=3, column=0)

        self.currency_combobox = ttk.Combobox(self.root, state='readonly')
        self.currency_combobox.grid(row=5, column=0)
        self.currency_dict = {'USD': '$', 'RUB': '₽', 'EUR': '€', 'Все вакансии': ''}
        self.currency_combobox['values'] = list(self.currency_dict.keys())
        self.currency_combobox.current(3)

        self.pages_combobox = ttk.Combobox(self.root, state='readonly')
        self.pages_combobox.set(1)
        self.pages_combobox.grid(row=7, column=0)

        self.btn = tk.Button(self.root, text="Поиск", command=self.search)
        self.btn.grid(row=9, column=0)

        self.btn_upload = tk.Button(self.root, text="Выгрузить в JSON", command=self.upload)
        self.btn_upload.grid(row=11, column=0)

        self.tree = ttk.Treeview(self.root, show='headings', columns=(1, 2, 3, 4, 5), height=20)
        column_widths = [120, 120, 120, 120, 120]
        for i, width in enumerate(column_widths):
            self.tree.column(i + 1, width=width)
        self.tree.grid(row=0, column=1, columnspan=5, rowspan=20)
        self.tree.tag_configure("url_tag", foreground="blue")

        self.tree.tag_bind("url_tag", "<Double-1>", self.on_tree_double_click)

        headings = ['Ссылка', 'Название', 'Компания', 'Зарплата', 'Город']
        for i, text in enumerate(headings):
            self.tree.heading(i + 1, text=text)
    @logger
    def on_tree_double_click(self, event):

        selected_item = self.tree.selection()

        if selected_item:
            values = self.tree.item(selected_item)['values']
            link = values[0]
            webbrowser.open(link)

    def search(self):
        data = Scraper(self.search_word_entry.get(), self.extra_words_entry.get().split(' '),
                       self.currency_dict.get(self.currency_combobox.get()),
                       self.pages_combobox.get()).get_vacancies()

        for idx, vacancy in enumerate(data):
            self.tree.insert('', 'end', text=str(idx), values=(
                vacancy["link"], vacancy["title"], vacancy["company"], vacancy["salary"], vacancy["city"]),
                tags=("url_tag",))

    def upload(self):
        data = []
        for child in self.tree.get_children():
            item = self.tree.item(child)
            values = item['values']
            data.append({
                "link": values[0],
                "title": values[1],
                "company": values[2],
                "salary": values[3],
                "city": values[4]
            })
        with open('vacancies.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':

    app = Inter()
