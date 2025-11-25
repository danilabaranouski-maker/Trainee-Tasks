import mysql.connector
import time

class DatabaseConnector:

    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    def __enter__(self):
        retries = 5
        for i in range(retries):
            try:
                self.conn = mysql.connector.connect(**self.config)
                self.cursor = self.conn.cursor()
                if i > 0:
                    print(f"Подключение к базе данных успешно после {i+1} попыток.")
                return self.cursor
            except mysql.connector.Error as err:
                print(f"Ошибка подключения (попытка {i+1}/{retries}): {err}")
                if i < retries - 1:
                    time.sleep(5)
                else:
                    print("Не удалось подключиться к базе данных после нескольких попыток.")
                    raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Метод вызывается при выходе из блока `with`.
        Закрывает соединение и курсор, делает commit или rollback.
        """
        if self.conn and self.conn.is_connected():
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()

            self.cursor.close()
            self.conn.close()
        return False