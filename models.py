import sqlite3
import logging

# Настройка логирования
logging.basicConfig(
    filename='irama.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Employee:
    def __init__(self, surname, name, patronymic, status, department):
        self.full_name = f"{surname} {name} {patronymic}" if patronymic else f"{surname} {name}"
        self.status = status
        self.department = department

    def save(self):
        try:
            conn = sqlite3.connect('irama.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO employees (name, status, department) VALUES (?, ?, ?)''',
                           (self.full_name, self.status, self.department))
            conn.commit()
            logging.info(f"Сотрудник {self.full_name} успешно добавлен.")
        except sqlite3.IntegrityError:
            logging.error("Ошибка: Сотрудник с таким именем уже существует.")
        except Exception as e:
            logging.error(f"Ошибка при добавлении сотрудника: {e}")
        finally:
            conn.close()

class Shift:
    def __init__(self, employee_id, shift_date, start_time, end_time):
        self.employee_id = employee_id
        self.shift_date = shift_date
        self.start_time = start_time
        self.end_time = end_time

    def save(self):
        try:
            conn = sqlite3.connect('irama.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO shifts (employee_id, shift_date, start_time, end_time) VALUES (?, ?, ?, ?)''',
                           (self.employee_id, self.shift_date, self.start_time, self.end_time))
            conn.commit()
            logging.info(f"Смена для сотрудника {self.employee_id} успешно добавлена.")
        except Exception as e:
            logging.error(f"Ошибка при добавлении смены: {e}")
        finally:
            conn.close()

class Attendance:
    def __init__(self, employee_id, shift_id, check_in_time, check_out_time=None):
        self.employee_id = employee_id
        self.shift_id = shift_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time

    def save(self):
        try:
            conn = sqlite3.connect('irama.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO attendance (employee_id, shift_id, check_in_time, check_out_time) VALUES (?, ?, ?, ?)''',
                           (self.employee_id, self.shift_id, self.check_in_time, self.check_out_time))
            conn.commit()
            logging.info(f"Запись о посещаемости для сотрудника {self.employee_id} успешно добавлена.")
        except Exception as e:
            logging.error(f"Ошибка при добавлении посещаемости: {e}")
        finally:
            conn.close()