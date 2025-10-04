import requests
from bs4 import BeautifulSoup
import json
import time

# --- Константы ---
# ВАЖНО: Используем русскую версию каталога, судя по предоставленному HTML-коду
x = "backend"
BASE_CATALOG_URL = f'https://www.rabota.md/ro/jobs-moldova-{x}'
BASE_URL = 'https://www.rabota.md'
PAGES_TO_SCRAPE = 2  # Количество страниц, которое нужно обработать (измените на 4 или более)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 1. ШАГ 1: АВТОМАТИЧЕСКИЙ СБОР ССЫЛОК СО ВСЕХ СТРАНИЦ
# =========================================================

all_vacancy_urls = set()  # Множество для хранения всех уникальных ссылок
print(f"Начинаю сбор ссылок с {PAGES_TO_SCRAPE} страниц, начиная с: {BASE_CATALOG_URL}")

for page_num in range(1, PAGES_TO_SCRAPE + 1):

    if page_num == 1:
        catalog_url = BASE_CATALOG_URL
    else:
        # Пагинация для русской версии: /ru/vacancies/category/it/2
        catalog_url = f"{BASE_CATALOG_URL}/{page_num}"

    print(f"\n---> Обрабатываю страницу {page_num}: {catalog_url}")

    try:
        response = requests.get(catalog_url, headers=headers)
        response.raise_for_status()

        catalog_soup = BeautifulSoup(response.text, 'html.parser')

        # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: УНИВЕРСАЛЬНЫЙ ФИЛЬТР ССЫЛОК ---
        # Ищем все теги <a>, которые имеют класс 'vacancyShowPopup'.
        links_found_on_page = 0
        for link_tag in catalog_soup.select('a.vacancyShowPopup'):
            href = link_tag.get('href')

            # Проверяем, содержит ли ссылка ЛЮБОЙ из известных паттернов
            is_valid_vacancy_path = (
                    '/joburi/' in href or
                    '/vacancies/' in href or
                    '/locuri-de-munca/' in href  # <--- ДОБАВЛЕНО ЭТО УСЛОВИЕ
            )

            # Дополнительная проверка на достаточную длину пути, чтобы отсеять категории.
            if href and is_valid_vacancy_path and len(href.split('/')) > 4:
                full_url = f"{BASE_URL}{href}" if href.startswith('/') else href
                all_vacancy_urls.add(full_url)
                links_found_on_page += 1

        print(f"   ✅ Найдено {links_found_on_page} ссылок. Всего уникальных ссылок: {len(all_vacancy_urls)}")

        time.sleep(1.5)

    except requests.exceptions.HTTPError as http_err:
        print(f"   ❌ Ошибка HTTP при сборе ссылок со страницы {page_num}: {http_err}")
        if response.status_code == 404:
            print("   Предполагаю, что достигнута последняя страница. Прерываю сбор ссылок.")
            break
    except Exception as err:
        print(f"   ❌ Произошла ошибка при сборе ссылок со страницы {page_num}: {err}")
        time.sleep(2)

# 2. ШАГ 2: Скрапинг каждой отдельной вакансии
# =========================================================

all_vacancies = []

if not all_vacancy_urls:
    print("\n⚠️ Список ссылок пуст. Нечего обрабатывать.")
else:
    print(f"\n--- Начинаю обработку {len(all_vacancy_urls)} собранных вакансий ---")

    for i, url in enumerate(all_vacancy_urls):
        print(i)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Извлечение данных ---
            title_tag = soup.find('h1', class_=['vacancy-title' , "text-3xl"])
            title = title_tag.get_text(strip=True) if title_tag else 'Название не найдено'

            # --- ГИБКИЙ ПОИСК ОПИСАНИЯ ---
            description = 'Описание не найдено'
            description_div = soup.find('div', class_= ['vacancy-content', 'inbody'])

            if description_div:
                description = description_div.get_text('\n', strip=True)

            vacancy_data = {
                'url': url,
                'title': title,
                'description': description,
                "category" : "Technical",
                "branch" : x
            }

            all_vacancies.append(vacancy_data)
            time.sleep(1)

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ Ошибка HTTP при обработке {url}: {http_err}")
        except Exception as err:
            print(f"❌ Произошла ошибка при обработке {url}: {err}")

# 3. ШАГ 3: Сохранение данных
# =========================================================

if all_vacancies:
    file_name = 'all_vacancies_final.json'
    with open(file_name, 'a', encoding='utf-8') as f:
        json.dump(all_vacancies, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 Все данные ({len(all_vacancies)} вакансий) успешно сохранены в файл: {file_name}")
else:
    print("\n⚠️ Не было собрано никаких данных для сохранения.")