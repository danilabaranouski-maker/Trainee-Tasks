import unittest
import json
import mysql.connector
from unittest.mock import MagicMock, patch, mock_open, call
from decimal import Decimal

from database import DatabaseConnector
from loader import DataLoader
import main
import sql_queries as sql

class TestApp(unittest.TestCase):

    # тест подключения к бд
    @patch('mysql.connector.connect')
    def test_db_retry_success(self, mock_connect):
        mock_connect.side_effect = [
            mysql.connector.Error("Connection Fail 1"),
            mysql.connector.Error("Connection Fail 2"),
            MagicMock()
        ]
        
        with patch('time.sleep', return_value=None):
            db = DatabaseConnector({'user': 'test'})
            with db:
                pass 
        
        self.assertEqual(mock_connect.call_count, 3)

    @patch('mysql.connector.connect')
    def test_db_commit_on_exit(self, mock_connect):
        mock_conn_instance = MagicMock()
        mock_connect.return_value = mock_conn_instance
        
        with DatabaseConnector({'user': 'test'}):
            pass
            
        mock_conn_instance.commit.assert_called_once()
        mock_conn_instance.close.assert_called_once()

    # тесты loader
    @patch('loader.DatabaseConnector')
    def test_loader_sql_generation(self, MockDB):
        mock_cursor = MockDB.return_value.__enter__.return_value
        
        fake_students = json.dumps([{
            "id": 1, "name": "Ivan", "birthday": "2000-01-01T00:00:00", 
            "sex": "M", "room": 10
        }])
        fake_rooms = json.dumps([{"id": 10, "name": "Room A"}])

        def side_effect_open(filename, *args, **kwargs):
            if 'students' in filename:
                return mock_open(read_data=fake_students).return_value
            return mock_open(read_data=fake_rooms).return_value

        loader = DataLoader({})

        with patch("builtins.open") as mock_file:
            mock_file.side_effect = side_effect_open
            loader.load_data('rooms.json', 'students.json')

        found_date = False
        for call_args in mock_cursor.execute.call_args_list:
            if len(call_args[0]) > 1:
                params = call_args[0][1]
                if isinstance(params, (list, tuple)) and "Ivan" in params:
                    self.assertEqual(params[2], "2000-01-01")
                    found_date = True
        
        self.assertTrue(found_date, "Дата студента не была корректно обработана")

    # тесты main
    @patch('main.save_as_json')
    @patch('main.DatabaseConnector')
    def test_decimal_to_float_conversion(self, MockDB, MockSave):
        mock_cursor = MockDB.return_value.__enter__.return_value
        
        mock_cursor.description = [('avg_age',)]
        mock_cursor.fetchall.return_value = [(Decimal('20.55'),)]
        
        with patch.dict('main.queries', {'test_out.json': 'SELECT 1'}):
            main.execute_and_save_queries('json')
        
        saved_data = MockSave.call_args[0][0] 
        value = saved_data[0]['avg_age']
        
        self.assertIsInstance(value, float)
        self.assertEqual(value, 20.55)

    def test_xml_export_structure(self):
        data = [{"id": 1, "name": "Test"}]
        
        with patch("builtins.open", mock_open()) as mocked_file:
            main.save_as_xml(data, "output.xml")
            
            handle = mocked_file()
            content = "".join(call.args[0] for call in handle.write.call_args_list)
            
            self.assertIn("<results>", content)
            self.assertIn("<item>", content)
            self.assertIn("<name>Test</name>", content)

if __name__ == '__main__':
    unittest.main()