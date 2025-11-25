# main.py

# --- 1. Импорты ---
# Стандартные библиотеки
import os
import json
from decimal import Decimal
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Сторонние библиотеки
import mysql.connector
from dotenv import load_dotenv

# Собственные модули
from loader import DataLoader
from database import DatabaseConnector
import sql_queries as sql

# --- 2. Начальная настройка ---

# ИЗМЕНЕНИЕ: Загружаем переменные из .env файла в окружение.
# Это делает код безопаснее, убирая пароли из исходного кода.
load_dotenv()

# ИЗМЕНЕНИЕ: Конфигурация для подключения к БД теперь читается из переменных окружения.
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Оставляем парсер аргументов для указания путей к файлам с данными.
# Аргумент --format теперь не так важен из-за интерактивного меню, но может быть полезен в будущем.
parser = argparse.ArgumentParser(description="Data loader and query executor")
parser.add_argument('--students', default='students.json', help='Путь к students.json')
parser.add_argument('--rooms', default='rooms.json', help='Путь к rooms.json')
parser.add_argument('--format', default='json', choices=['json', 'xml'], help='Формат вывода по умолчанию')
args = parser.parse_args()

# ИЗМЕНЕНИЕ: Словарь с запросами теперь использует переменные из sql_queries.py.
# Это делает код чище и упрощает управление SQL-запросами.
queries = {
    "res1.json": sql.QUERY_1,
    "res2.json": sql.QUERY_2,
    "res3.json": sql.QUERY_3,
    "res4.json": sql.QUERY_4
}


# --- 3. Вспомогательные функции ---

# НОВОЕ: Функция для сохранения в JSON. Вынесена из основного цикла для чистоты кода.
def save_as_json(data, filename):
    """Сохраняет список словарей в JSON-файл."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# НОВОЕ: Функция для сохранения в XML. Добавлена для расширения функционала.
def save_as_xml(data, filename):
    """Сохраняет список словарей в XML-файл."""
    root = ET.Element('results')
    for item_dict in data:
        item_element = ET.Element('item')
        root.append(item_element)
        for key, value in item_dict.items():
            child = ET.Element(key)
            child.text = str(value)
            item_element.append(child)

    xml_string = ET.tostring(root, 'utf-8')
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)


# НОВОЕ: Основная логика по выполнению запросов вынесена в отдельную функцию.
# Это ключевое изменение для создания интерактивного меню.
def execute_and_save_queries(output_format):
    """Выполняет все запросы и сохраняет их в указанном формате."""
    try:
        with DatabaseConnector(db_config) as cursor:
            print(f"\nВыполняю запросы и сохраняю в формате {output_format.upper()}...")
            for filename_base, sql_query in queries.items():
                cursor.execute(sql_query)
                column_names = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()

                # Преобразуем результаты (кортежи) в список словарей
                result_list = []
                for row in results:
                    row_dict = dict(zip(column_names, row))
                    for key, value in row_dict.items():
                        if isinstance(value, Decimal):
                            row_dict[key] = float(value)
                    result_list.append(row_dict)

                # Формируем имя файла и вызываем нужную функцию сохранения
                output_filename = filename_base.replace('.json', f'.{output_format}')
                if output_format == 'json':
                    save_as_json(result_list, output_filename)
                elif output_format == 'xml':
                    save_as_xml(result_list, output_filename)
                print(f" -> Результат сохранен в {output_filename}")
        print("Все запросы выполнены.")
    except mysql.connector.Error as err:
        print(f"Ошибка базы данных: {err}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# --- 4. Главная функция и цикл программы ---

# НОВОЕ: Создана главная функция main() для структурирования кода.
def main():
    """Главная функция программы."""
    # Шаг 1: Загрузка данных в базу данных. Выполняется один раз при старте.
    print("Загрузка данных в базу...")
    loader = DataLoader(db_config)
    loader.create_tables()
    loader.load_data(args.rooms, args.students)
    print("-" * 30)

    # Шаг 2: Запуск интерактивного меню в бесконечном цикле.
    # Программа будет работать, пока пользователь не решит выйти.
    while True:
        print("\nВыберите действие:")
        print("1. Выполнить запросы и сохранить результаты")
        print("2. Выйти из программы")
        choice = input("Введите номер действия: ")

        if choice == '1':
            # Вложенный цикл для выбора формата сохранения
            format_choice = ''
            while format_choice not in ['json', 'xml']:
                format_choice = input("В каком формате сохранить? (json/xml): ").lower()
                if format_choice not in ['json', 'xml']:
                    print("Неверный формат. Пожалуйста, выберите 'json' или 'xml'.")

            # Вызываем функцию выполнения запросов с выбранным форматом
            execute_and_save_queries(format_choice)

        elif choice == '2':
            # Выход из бесконечного цикла
            print("Завершение работы.")
            break
        else:
            # Обработка неверного ввода
            print("Неверный ввод. Пожалуйста, выберите 1 или 2.")


# --- 5. Точка входа в программу ---

# Эта стандартная конструкция Python гарантирует, что функция main()
# будет вызвана только тогда, когда этот файл запускается напрямую.
if __name__ == "__main__":
    main()