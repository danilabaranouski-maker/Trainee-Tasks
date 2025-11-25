import json
from database import DatabaseConnector
import sql_queries as sql

class DataLoader:
    """
    Класс для загрузки данных из JSON-файлов в базу данных.
    """

    def __init__(self, db_config):
        """
        Инициализация загрузчика с параметрами подключения.
        """
        self.db_config = db_config

        # SQL-запросы для вставки данных
        self.sql_insert_room = sql.INSERT_ROOM
        self.sql_insert_student = sql.INSERT_STUDENT

    def create_tables(self):
        """
        Создаёт таблицы, если их нет.
        """
        with DatabaseConnector(self.db_config) as cursor:
            cursor.execute(sql.CREATE_ROOMS_TABLE)
            cursor.execute(sql.CREATE_STUDENTS_TABLE)
            print("Таблицы проверены или созданы.")

    def load_data(self, rooms_path, students_path):
        """
        Загружает данные из JSON-файлов в таблицы.
        :param rooms_path: путь к файлу rooms.json
        :param students_path: путь к файлу students.json
        """
        db_connector = DatabaseConnector(self.db_config)

        try:
            with db_connector as cursor:
                # Отключаем проверки внешних ключей и очищаем таблицы
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("TRUNCATE TABLE rooms;")
                cursor.execute("TRUNCATE TABLE students;")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

                # Загружаем комнаты
                with open(rooms_path, 'r', encoding='utf-8') as f:
                    rooms_data = json.load(f)
                for room in rooms_data:
                    cursor.execute(self.sql_insert_room, (room['id'], room['name']))
                print(f"Загружено комнат: {len(rooms_data)}")

                with open(students_path, 'r', encoding='utf-8') as f:
                    students_data = json.load(f)
                for student in students_data:
                    correct_date = student['birthday'].split('T')[0]
                    student_values = (student['id'], student['name'], correct_date, student['sex'], student['room'])
                    cursor.execute(self.sql_insert_student, student_values)
                print(f"Загружено студентов: {len(students_data)}")

            print("Загрузка данных завершена.")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
