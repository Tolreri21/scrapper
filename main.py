import requests
from bs4 import BeautifulSoup
import json
import time

# --- Константы ---
# Базовый URL страницы, который будет дополняться номером страницы
BASE_CATALOG_URL = 'https://www.rabota.md/ro/vacancies/category/it'
BASE_URL = 'https://www.rabota.md'
PAGES_TO_SCRAPE = 1  # Количество страниц, которые нужно обработать (от 1 до 4)

# Заголовки для имитации запроса от браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 1. ШАГ 1: АВТОМАТИЧЕСКИЙ СБОР ССЫЛОК СО ВСЕХ СТРАНИЦ
# =========================================================

all_vacancy_urls = set()  # Множество для хранения всех уникальных ссылок
print(f"Начинаю сбор ссылок с {PAGES_TO_SCRAPE} страниц, начиная с: {BASE_CATALOG_URL}")

# Цикл для перебора страниц (от 1 до PAGES_TO_SCRAPE включительно)
for page_num in range(1, PAGES_TO_SCRAPE + 1):

    # Формируем URL страницы. Первая страница (page_num=1) не имеет /1,
    # поэтому добавляем номер только для страниц 2 и далее.
    if page_num == 1:
        catalog_url = BASE_CATALOG_URL
    else:
        catalog_url = f"{BASE_CATALOG_URL}/{page_num}"

    print(f"\n---> Обрабатываю страницу {page_num}: {catalog_url}")

    try:
        # Отправляем GET-запрос
        response = requests.get(catalog_url, headers=headers)
        response.raise_for_status()  # Проверка на ошибки HTTP

        catalog_soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все теги <a>, которые ведут на отдельные вакансии
        # Селектор: ищем теги <a> с href, содержащим '/vacancies/'
        links_found_on_page = 0
        for link_tag in catalog_soup.select('a[href*="/vacancies/"]'):
            href = link_tag.get('href')

            # Фильтруем, чтобы брать только ссылки на отдельные вакансии
            if '/vacancies/' in href and not href.endswith('vacancies'):
                # Создаем полный URL
                full_url = f"{BASE_URL}{href}" if href.startswith('/') else href
                all_vacancy_urls.add(full_url)
                links_found_on_page += 1

        print(f"   ✅ Найдено {links_found_on_page} ссылок. Всего уникальных ссылок: {len(all_vacancy_urls)}")

        # Обязательная задержка между запросами к каталогу
        time.sleep(1.5)

    except requests.exceptions.HTTPError as http_err:
        print(f"   ❌ Ошибка HTTP при сборе ссылок со страницы {page_num}: {http_err}")
        # Если страница не найдена (например, страница 50 не существует),
        # имеет смысл прервать цикл, так как дальше страниц, скорее всего, нет.
        if response.status_code == 404:
            print("   Предполагаю, что достигнута последняя страница. Прерываю сбор ссылок.")
            break
    except Exception as err:
        print(f"   ❌ Произошла ошибка при сборе ссылок со страницы {page_num}: {err}")
        time.sleep(2)  # Даем чуть больше времени, если была ошибка, прежде чем продолжить

# 2. ШАГ 2: Скрапинг каждой отдельной вакансии
# =========================================================

# Общий список для хранения всех данных о вакансиях
all_vacancies = []

if not all_vacancy_urls:
    print("\n⚠️ Список ссылок пуст. Нечего обрабатывать.")
else:
    print(f"\n--- Начинаю обработку {len(all_vacancy_urls)} собранных вакансий ---")

    for url in all_vacancy_urls:
        try:
            # Отправляем GET-запрос на страницу
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Извлечение данных ---
            title_tag = soup.find('h1', class_='vacancy-title')
            title = title_tag.get_text(strip=True) if title_tag else 'Название не найдено'

            description_div = soup.find('div', class_='inbody')
            description = description_div.get_text('\n', strip=True) if description_div else 'Описание не найдено'

            # Сохраняем извлеченные данные
            vacancy_data = {
                'url': url,
                'title': title,
                'description': description
            }

            all_vacancies.append(vacancy_data)

            # print(f"✅ Успешно обработан URL: {url}")

            # !!! Важно: задержка между запросами к отдельным вакансиям
            time.sleep(1)

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ Ошибка HTTP при обработке {url}: {http_err}")
        except Exception as err:
            print(f"❌ Произошла ошибка при обработке {url}: {err}")

# 3. ШАГ 3: Сохранение данных
# =========================================================

if all_vacancies:
    file_name = 'all_vacancies_paginated.json'
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(all_vacancies, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 Все данные ({len(all_vacancies)} вакансий) успешно сохранены в файл: {file_name}")
else:
    print("\n⚠️ Не было собрано никаких данных для сохранения.")