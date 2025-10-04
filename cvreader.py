import os
import re

try:
    from pypdf import PdfReader
except ImportError:
    print("Библиотека 'pypdf' не найдена. Установите ее командой: pip install pypdf")


    # Создаем заглушку, чтобы программа могла запуститься и показать, что нужно установить
    class PdfReader:
        def __init__(self, *args, **kwargs):
            raise ImportError("pypdf is not installed.")


# --- Утилита для очистки LaTeX ---

def clean_latex_text(latex_content: str) -> str:
    """
    Удаляет команды и разметку LaTeX, оставляя только чистый текст.
    Возвращает очищенную строку.
    """

    # 1. Удаляем комментарии (начиная с % до конца строки)
    content = re.sub(r'%.*?\n', '\n', latex_content)

    # 2a. Удаляем команды, которые обычно содержат метаданные (documentclass, usepackage, geometry, title, author, date)
    content = re.sub(r'\\(documentclass|usepackage|geometry|title|author|date)\{[^}]*\}', ' ', content)

    # 2b. Обрабатываем \href{URL}{Текст}. Оставляем только Текст.
    content = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', content)

    # 2c. Обрабатываем \textbf{Текст}, \section{Текст} и т.д., оставляя только текст внутри {}.
    # Используем нежадный захват: \команда{текст} -> текст
    content = re.sub(r'\\(\w+)\*?\{([^}]*)\}', r'\2', content)

    # 3. Удаляем оставшиеся простые команды (\begin, \end, \item, \maketitle, \hfill, \\)
    content = re.sub(r'\\[a-zA-Z]+\*?', ' ', content)

    # 4. Удаляем символы разметки, которые могли остаться: { } [ ] &
    content = re.sub(r'[{}|\\\[\]&]', ' ', content)

    # 5. Очищаем пробелы и переводы строк, оставляя только один пробел между словами
    content = re.sub(r'\s+', ' ', content).strip()

    return content


# --- Функции для чтения файлов ---

def read_pdf_cv(filepath: str) -> str:
    """
    Извлекает текст из PDF-файла и возвращает его как одну строку.

    В контексте backend: эта функция будет вызываться, когда веб-сервер
    получает путь к сохраненному PDF-файлу.
    """
    print(f"\n--- Чтение PDF файла: {filepath} ---")

    if not os.path.exists(filepath):
        # В реальном backend вы бы вернули ошибку HTTP 404/500
        return f"Ошибка: Файл PDF не найден по пути: {filepath}"

    full_text = ""
    try:
        reader = PdfReader(filepath)
        num_pages = len(reader.pages)

        for i in range(num_pages):
            page = reader.pages[i]
            # Добавляем текст страницы и разделитель (например, новую строку)
            full_text += page.extract_text() + "\n---\n"

        return full_text.strip()

    except ImportError:
        return "Ошибка: Не удалось прочитать PDF. Проверьте установку 'pypdf'."
    except Exception as e:
        return f"Произошла ошибка при чтении PDF: {e}"


def read_latex_cv(filepath: str) -> str:
    """
    Читает содержимое LaTeX-файла (.tex), удаляет разметку и возвращает чистый текст.

    В контексте backend: эта функция будет вызываться, когда веб-сервер
    получает путь к сохраненному LaTeX-файлу.
    """
    print(f"\n--- Чтение и очистка LaTeX файла: {filepath} ---")

    if not os.path.exists(filepath):
        # В реальном backend вы бы вернули ошибку HTTP 404/500
        return f"Ошибка: Файл LaTeX не найден по пути: {filepath}"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            latex_content = f.read()
            # Применяем очистку и возвращаем чистый текст
            return clean_latex_text(latex_content)

    except UnicodeDecodeError:
        # Добавляем обработку ошибки кодировки
        return f"Ошибка кодировки: Не удалось прочитать файл '{filepath}' как UTF-8. Убедитесь, что это текстовый файл (.tex), а не бинарный (например, PDF)."
    except Exception as e:
        return f"Произошла ошибка при чтении LaTeX файла: {e}"


# --- Функция для сохранения обработанного контента ---

def save_processed_content(text_data: str, filename: str) -> None:
    """
    Сохраняет обработанный текст в указанный файл на диске.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_data)
        print(f"[Сохранение] Успешно сохранен чистый текст в файл: {filename}")
    except Exception as e:
        print(f"[Ошибка сохранения] Не удалось сохранить файл {filename}: {e}")


# --- Пример интеграции в backend ---

if __name__ == "__main__":
    print("--- Имитация работы Backend-процессора CV ---")
    print("---------------------------------------------")

    # 1. Задаем гипотетические пути, которые мог бы предоставить веб-фреймворк
    uploaded_pdf_path = "user_cvs/a1b2c3d4e5/resume_v1.pdf"
    uploaded_latex_path = "user_cvs/a1b2c3d4e5/source_cv.tex"

    # --- Имитация чтения и обработки ---
    # Мы используем фиктивный контент, так как файлы не существуют,
    # но в реальном backend тут будут вызваны read_pdf_cv и read_latex_cv

    mock_pdf_output = "Имитация текста из PDF: Программист, Python, 5 лет опыта."
    mock_latex_output = "Имитация чистого текста из LaTeX: Junior Developer, Java, SQL, Git."

    print(f"\n[Backend] Обработка PDF CV завершена. Текст получен.")

    # Сохраняем обработанный PDF текст в файл
    output_pdf_file = "processed_output_pdf.txt"
    save_processed_content(mock_pdf_output, output_pdf_file)

    print("-" * 20)

    print(f"[Backend] Обработка LaTeX CV завершена. Чистый текст получен.")

    # Сохраняем обработанный LaTeX текст в файл
    output_latex_file = "processed_output_latex.txt"
    save_processed_content(mock_latex_output, output_latex_file)

    print("\n---------------------------------------------")
    print("Теперь обработанный контент сохранен на диске.")
