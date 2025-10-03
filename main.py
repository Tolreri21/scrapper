import requests
from bs4 import BeautifulSoup
import json

# URL конкретной вакансии для примера
# Замените этот URL на тот, который вас интересует
url = 'https://www.rabota.md/ro/locuri-de-munca/reactjs-developer/72315'

# Заголовки для имитации запроса от браузера, чтобы избежать блокировки
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Словарь для хранения данных о вакансии
vacancy_data = {}

try:
    # Отправляем GET-запрос на страницу
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Проверяем, успешен ли запрос (код 200)

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Извлечение данных ---

    # 1. Название вакансии
    # Ищем заголовок h1 с классом 'vacancy-title'
    # Ищем тег h1 с классом 'vacancy-title'
    title_tag = soup.find('h1', class_='vacancy-title')
    title = title_tag.get_text(strip=True) if title_tag else 'Название не найдено'

    # 2. Описание вакансии
    # Описание обычно находится в div с классом 'vacancy-description'
    description_div = soup.find('div', class_='inbody')
    description = description_div.get_text('\n', strip=True) if description_div else 'Описание не найдено'

    # Сохраняем извлеченные данные в словарь
    vacancy_data = {
        'url': url,
        'title': title,
        'description': description
    }

    # --- Сохранение в JSON ---

    # Имя файла для сохранения
    file_name = 'vacancy_description.json'

    # Сохраняем словарь в файл JSON
    with open(file_name, 'w', encoding='utf-8') as f:
        # indent=4 для красивого форматирования, ensure_ascii=False для корректного отображения кириллицы
        json.dump(vacancy_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Данные успешно сохранены в файл: {file_name}")
    print(json.dumps(vacancy_data, ensure_ascii=False, indent=4))


except requests.exceptions.HTTPError as http_err:
    print(f"❌ Ошибка HTTP: {http_err}")
except Exception as err:
    print(f"❌ Произошла ошибка: {err}")