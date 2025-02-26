import sqlite3
import logging
from datetime import datetime
import shutil

# Настройка логирования
logging.basicConfig(
    filename='irama.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def create_connection():
    """Создаёт соединение с SQLite."""
    try:
        conn = sqlite3.connect('irama.db')
        logging.info("Соединение с SQLite установлено.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Ошибка подключения к SQLite: {e}")
        return None

def create_tables():
    """Создаёт таблицы в базе данных."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                shift_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                shift_id INTEGER NOT NULL,
                check_in_time DATETIME NOT NULL,
                check_out_time DATETIME,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
                FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
        logging.info("Таблицы успешно созданы.")
    else:
        logging.error("Не удалось создать таблицы, так как соединение не установлено.")

def backup_database():
    """Создаёт резервную копию базы данных."""
    try:
        backup_filename = f"irama_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('irama.db', backup_filename)
        logging.info(f"Резервная копия создана: {backup_filename}")
    except Exception as e:
        logging.error(f"Ошибка при создании резервной копии: {e}")

if __name__ == "__main__":
    create_tables()  # Создание таблиц при запуске
    backup_database()  # Создание резервной копии