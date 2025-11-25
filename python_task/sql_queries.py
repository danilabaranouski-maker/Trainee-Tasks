CREATE_ROOMS_TABLE = """
    CREATE TABLE IF NOT EXISTS rooms (
        id INT PRIMARY KEY,
        name VARCHAR(255)
    );
"""

CREATE_STUDENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS students (
        id INT PRIMARY KEY,
        name VARCHAR(255),
        birthday DATE,
        sex ENUM('M', 'F'),
        room_id INT,
        FOREIGN KEY (room_id) REFERENCES rooms(id)
    );
"""

INSERT_ROOM = 'INSERT INTO rooms (id, name) VALUES (%s, %s)'

INSERT_STUDENT = '''
    INSERT INTO students (id, name, birthday, sex, room_id)
    VALUES (%s, %s, %s, %s, %s)
'''

QUERY_1 = """
    SELECT r.name AS room_name, COUNT(s.id) AS students_count
    FROM rooms r LEFT JOIN students s ON r.id = s.room_id
    GROUP BY r.name ORDER BY r.name ASC;
"""

QUERY_2 = """
    SELECT r.name AS room_name, AVG(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) AS avg_age
    FROM rooms r INNER JOIN students s ON r.id = s.room_id
    GROUP BY r.name ORDER BY avg_age ASC LIMIT 5;
"""

QUERY_3 = """
    SELECT r.name AS room_name,
           (MAX(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) - MIN(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE()))) AS age_diff
    FROM rooms r JOIN students s ON r.id = s.room_id
    GROUP BY r.name HAVING COUNT(s.id) > 1
    ORDER BY age_diff DESC LIMIT 5;
"""

QUERY_4 = """
    SELECT r.name AS room_name
    FROM rooms r INNER JOIN students s ON r.id = s.room_id
    GROUP BY r.name HAVING COUNT(DISTINCT s.sex) > 1;
"""