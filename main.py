import sqlite3
from database import create_connection, backup_database
from models import Employee, Shift, Attendance
import csv
import logging

# Настройка логирования
logging.basicConfig(
    filename='irama.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def add_employee(surname, name, patronymic, status, department):
    """Добавляет сотрудника в базу данных."""
    try:
        full_name = f"{surname} {name} {patronymic}" if patronymic else f"{surname} {name}"
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO employees (name, status, department) VALUES (?, ?, ?)''',
                           (full_name, status, department))
            conn.commit()
            logging.info(f"Сотрудник {full_name} успешно добавлен.")
    except sqlite3.IntegrityError:
        logging.error("Ошибка: Сотрудник с таким именем уже существует.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении сотрудника: {e}")

def delete_employee(employee_id):
    """Удаляет сотрудника из базы данных."""
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM employees WHERE id = ?''', (employee_id,))
            conn.commit()
            logging.info(f"Сотрудник с ID {employee_id} успешно удалён.")
    except Exception as e:
        logging.error(f"Ошибка при удалении сотрудника: {e}")

def add_shift(employee_id, shift_date, start_time, end_time):
    """Добавляет смену в базу данных."""
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO shifts (employee_id, shift_date, start_time, end_time) VALUES (?, ?, ?, ?)''',
                           (employee_id, shift_date, start_time, end_time))
            conn.commit()
            logging.info(f"Смена для сотрудника {employee_id} успешно добавлена.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении смены: {e}")

def add_attendance(employee_id, shift_id, check_in_time, check_out_time=None):
    """Добавляет запись о посещаемости."""
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO attendance (employee_id, shift_id, check_in_time, check_out_time) VALUES (?, ?, ?, ?)''',
                           (employee_id, shift_id, check_in_time, check_out_time))
            conn.commit()
            logging.info(f"Запись о посещаемости для сотрудника {employee_id} успешно добавлена.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении посещаемости: {e}")

def generate_attendance_report(start_date, end_date):
    """Генерирует отчёт по посещаемости за указанный период."""
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.name, a.check_in_time, a.check_out_time
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
                WHERE a.check_in_time BETWEEN ? AND ?
            ''', (start_date, end_date))
            data = cursor.fetchall()

            # Сохранение в CSV
            with open("attendance_report.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Сотрудник", "Приход", "Уход"])
                writer.writerows(data)
            logging.info("Отчёт сохранён в attendance_report.csv")
    except Exception as e:
        logging.error(f"Ошибка: {e}")

if __name__ == "__main__":
    # Пример использования функций
    backup_database()  # Создаём резервную копию перед началом работы
    add_employee('Иванов', 'Иван', 'Иванович', 'Основной', 'Отдел продаж')
    add_shift(1, '2023-10-15', '09:00', '18:00')
    add_attendance(1, 1, '2023-10-15 09:00', '2023-10-15 18:00')
    generate_attendance_report('2023-10-01', '2023-10-31')