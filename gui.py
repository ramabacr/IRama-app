import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import logging
import csv
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from plyer import notification
import re
from tkcalendar import Calendar  # Импорт календаря

# Логирование
logging.basicConfig(filename='irama.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Подключение к базе данных
conn = sqlite3.connect("irama.db")
cursor = conn.cursor()

# Удаление и создание таблицы employees с новыми столбцами
cursor.execute("DROP TABLE IF EXISTS employees")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT,
        department TEXT,
        date_of_birth TEXT,
        city TEXT,
        phone_number TEXT,
        passport_data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        shift_date TEXT,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        shift_id INTEGER,
        check_in_time TEXT,
        check_out_time TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id),
        FOREIGN KEY (shift_id) REFERENCES shifts (id)
    )
''')

conn.commit()

class DatePicker:
    """Всплывающий календарь для выбора даты."""
    def __init__(self, parent, entry_widget):
        self.parent = parent
        self.entry_widget = entry_widget
        self.cal = None

    def show_calendar(self):
        """Открывает календарь для выбора даты."""
        def set_date():
            selected_date = cal.get_date()
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, selected_date.strftime('%d.%m.%Y'))  # Формат даты: дд.мм.гггг
            top.destroy()

        top = tk.Toplevel(self.parent)
        top.title("Выберите дату")
        cal = Calendar(
            top,
            selectmode="day",
            year=2000,
            month=1,
            day=1,
            mindate=datetime(1900, 1, 1),
            maxdate=datetime.today(),
            date_pattern="dd.MM.yyyy"
        )
        cal.pack(pady=10, padx=10)

        btn_ok = tk.Button(top, text="Выбрать", command=set_date)
        btn_ok.pack(pady=10)

class IRamaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("iRama – Управление персоналом")
        
        # Автоматическое разрешение экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        # Вкладки
        self.tab_control = ttk.Notebook(root)
        
        # Вкладка "Сотрудники"
        self.tab_employees = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_employees, text="Сотрудники")
        self.setup_employees_tab()
        
        # Вкладка "Смены"
        self.tab_shifts = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_shifts, text="Смены")
        self.setup_shifts_tab()
        
        # Вкладка "Посещаемость"
        self.tab_attendance = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_attendance, text="Посещаемость")
        self.setup_attendance_tab()
        
        # Вкладка "Отчёты"
        self.tab_reports = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_reports, text="Отчёты")
        self.setup_reports_tab()
        
        self.tab_control.pack(expand=1, fill="both")

    def setup_employees_tab(self):
        """Настройка вкладки 'Сотрудники'."""
        # Поиск сотрудника
        self.search_label = tk.Label(self.tab_employees, text="Поиск сотрудника:")
        self.search_label.pack(pady=5)
        
        self.search_entry = tk.Entry(self.tab_employees, width=40)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_employee)
        
        # Кнопки управления
        self.buttons_frame = tk.Frame(self.tab_employees)
        self.buttons_frame.pack(pady=10)
        
        self.add_button = tk.Button(self.buttons_frame, text="Добавить сотрудника", command=self.add_employee)
        self.add_button.grid(row=0, column=0, padx=10)
        
        self.edit_button = tk.Button(self.buttons_frame, text="Редактировать сотрудника", command=self.edit_employee)
        self.edit_button.grid(row=0, column=1, padx=10)
        
        self.delete_button = tk.Button(self.buttons_frame, text="Удалить сотрудника", command=self.delete_employee)
        self.delete_button.grid(row=0, column=2, padx=10)
        
        # Таблица сотрудников
        self.tree = ttk.Treeview(self.tab_employees, columns=("ID", "ФИО", "Статус", "Отдел", "Дата рождения", "Город", "Телефон", "Паспорт"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("ФИО", text="ФИО")
        self.tree.heading("Статус", text="Статус")
        self.tree.heading("Отдел", text="Отдел")
        self.tree.heading("Дата рождения", text="Дата рождения")
        self.tree.heading("Город", text="Город")
        self.tree.heading("Телефон", text="Телефон")
        self.tree.heading("Паспорт", text="Паспорт")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Загрузка данных
        self.load_employees()

    def load_employees(self):
        """Загружает сотрудников в таблицу."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        cursor.execute("SELECT * FROM employees")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def search_employee(self, event):
        """Поиск сотрудника по имени, отделу или статусу."""
        search_text = self.search_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        cursor.execute("SELECT * FROM employees WHERE name LIKE ? OR department LIKE ? OR status LIKE ?",
                       ('%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%'))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_employee(self):
        """Добавляет нового сотрудника."""
        def save_employee():
            surname = entry_surname.get()
            name = entry_name.get()
            patronymic = entry_patronymic.get()
            department = entry_department.get()
            status = combo_status.get()
            date_of_birth = entry_dob.get()
            city = entry_city.get()
            phone_number = entry_phone.get()
            passport_data = entry_passport.get()

            if surname and name and department and status:
                if not self.validate_date(date_of_birth):
                    messagebox.showwarning("Ошибка", "Некорректный формат даты! Используйте дд.мм.гггг.")
                    return
                if not self.validate_phone(phone_number):
                    messagebox.showwarning("Ошибка", "Некорректный номер телефона!")
                    return

                full_name = f"{surname} {name} {patronymic}" if patronymic else f"{surname} {name}"
                cursor.execute("""
                    INSERT INTO employees (name, status, department, date_of_birth, city, phone_number, passport_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (full_name, status, department, date_of_birth, city, phone_number, passport_data))
                conn.commit()
                logging.info(f"Добавлен новый сотрудник: {full_name}, отдел: {department}, статус: {status}")
                self.load_employees()
                add_window.destroy()
            else:
                messagebox.showwarning("Ошибка", "Заполните обязательные поля!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить сотрудника")
        add_window.geometry("800x800")

        tk.Label(add_window, text="Фамилия:").pack(pady=5)
        entry_surname = tk.Entry(add_window, width=30)
        entry_surname.pack(pady=5)
        
        tk.Label(add_window, text="Имя:").pack(pady=5)
        entry_name = tk.Entry(add_window, width=30)
        entry_name.pack(pady=5)
        
        tk.Label(add_window, text="Отчество:").pack(pady=5)
        entry_patronymic = tk.Entry(add_window, width=30)
        entry_patronymic.pack(pady=5)

        tk.Label(add_window, text="Отдел:").pack(pady=5)
        entry_department = tk.Entry(add_window, width=30)
        entry_department.pack(pady=5)

        tk.Label(add_window, text="Статус:").pack(pady=5)
        combo_status = ttk.Combobox(add_window, values=["Постоянный", "Сезонный"])
        combo_status.pack(pady=5)

        tk.Label(add_window, text="Дата рождения:").pack(pady=5)
        entry_dob = tk.Entry(add_window, width=30)
        entry_dob.pack(pady=5)

        # Кнопка для выбора даты
        btn_calendar = tk.Button(add_window, text="Выбрать дату", command=lambda: DatePicker(add_window, entry_dob).show_calendar())
        btn_calendar.pack(pady=5)

        tk.Label(add_window, text="Город:").pack(pady=5)
        entry_city = tk.Entry(add_window, width=30)
        entry_city.pack(pady=5)

        tk.Label(add_window, text="Номер телефона:").pack(pady=5)
        entry_phone = tk.Entry(add_window, width=30)
        entry_phone.pack(pady=5)

        tk.Label(add_window, text="Паспортные данные:").pack(pady=5)
        entry_passport = tk.Entry(add_window, width=30)
        entry_passport.pack(pady=5)

        btn_save = tk.Button(add_window, text="Сохранить", command=save_employee)
        btn_save.pack(pady=10)

    def edit_employee(self):
        """Редактирует данные сотрудника."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите сотрудника для редактирования!")
            return

        employee_id = self.tree.item(selected_item, "values")[0]
        cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        employee_data = cursor.fetchone()

        def save_edited_employee():
            surname = entry_surname.get()
            name = entry_name.get()
            patronymic = entry_patronymic.get()
            department = entry_department.get()
            status = combo_status.get()
            date_of_birth = entry_dob.get()
            city = entry_city.get()
            phone_number = entry_phone.get()
            passport_data = entry_passport.get()

            if surname and name and department and status:
                if not self.validate_date(date_of_birth):
                    messagebox.showwarning("Ошибка", "Некорректный формат даты! Используйте дд.мм.гггг.")
                    return
                if not self.validate_phone(phone_number):
                    messagebox.showwarning("Ошибка", "Некорректный номер телефона!")
                    return

                full_name = f"{surname} {name} {patronymic}" if patronymic else f"{surname} {name}"
                cursor.execute("""
                    UPDATE employees
                    SET name = ?, status = ?, department = ?, date_of_birth = ?, city = ?, phone_number = ?, passport_data = ?
                    WHERE id = ?
                """, (full_name, status, department, date_of_birth, city, phone_number, passport_data, employee_id))
                conn.commit()
                logging.info(f"Сотрудник {full_name} успешно обновлён.")
                self.load_employees()
                edit_window.destroy()
            else:
                messagebox.showwarning("Ошибка", "Заполните обязательные поля!")

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактировать сотрудника")
        edit_window.geometry("800x800")

        tk.Label(edit_window, text="Фамилия:").pack(pady=5)
        entry_surname = tk.Entry(edit_window, width=30)
        entry_surname.insert(0, employee_data[1].split()[0])
        entry_surname.pack(pady=5)
        
        tk.Label(edit_window, text="Имя:").pack(pady=5)
        entry_name = tk.Entry(edit_window, width=30)
        entry_name.insert(0, employee_data[1].split()[1])
        entry_name.pack(pady=5)
        
        tk.Label(edit_window, text="Отчество:").pack(pady=5)
        entry_patronymic = tk.Entry(edit_window, width=30)
        if len(employee_data[1].split()) > 2:
            entry_patronymic.insert(0, employee_data[1].split()[2])
        entry_patronymic.pack(pady=5)

        tk.Label(edit_window, text="Отдел:").pack(pady=5)
        entry_department = tk.Entry(edit_window, width=30)
        entry_department.insert(0, employee_data[3])
        entry_department.pack(pady=5)

        tk.Label(edit_window, text="Статус:").pack(pady=5)
        combo_status = ttk.Combobox(edit_window, values=["Постоянный", "Сезонный"])
        combo_status.set(employee_data[2])
        combo_status.pack(pady=5)

        tk.Label(edit_window, text="Дата рождения:").pack(pady=5)
        entry_dob = tk.Entry(edit_window, width=30)
        entry_dob.insert(0, employee_data[4])
        entry_dob.pack(pady=5)

        # Кнопка для выбора даты
        btn_calendar = tk.Button(edit_window, text="Выбрать дату", command=lambda: DatePicker(edit_window, entry_dob).show_calendar())
        btn_calendar.pack(pady=5)

        tk.Label(edit_window, text="Город:").pack(pady=5)
        entry_city = tk.Entry(edit_window, width=30)
        entry_city.insert(0, employee_data[5])
        entry_city.pack(pady=5)

        tk.Label(edit_window, text="Номер телефона:").pack(pady=5)
        entry_phone = tk.Entry(edit_window, width=30)
        entry_phone.insert(0, employee_data[6])
        entry_phone.pack(pady=5)

        tk.Label(edit_window, text="Паспортные данные:").pack(pady=5)
        entry_passport = tk.Entry(edit_window, width=30)
        entry_passport.insert(0, employee_data[7])
        entry_passport.pack(pady=5)

        btn_save = tk.Button(edit_window, text="Сохранить", command=save_edited_employee)
        btn_save.pack(pady=10)

    def delete_employee(self):
        """Удаляет сотрудника."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите сотрудника для удаления!")
            return

        employee_id = self.tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого сотрудника?")
        if confirm:
            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            conn.commit()
            self.load_employees()
            logging.info(f"Сотрудник с ID {employee_id} удалён.")

    def validate_date(self, date_str):
        """Проверяет, соответствует ли строка формату даты дд.мм.гггг."""
        try:
            datetime.strptime(date_str, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    def validate_phone(self, phone):
        """Проверяет, соответствует ли номер телефона формату."""
        pattern = r'^\+?\d{10,15}$'  # Пример: +79161234567 или 89161234567
        return re.match(pattern, phone) is not None

    def setup_shifts_tab(self):
        """Настройка вкладки 'Смены'."""
        pass  # Реализуйте эту функцию, если нужно

    def setup_attendance_tab(self):
        """Настройка вкладки 'Посещаемость'."""
        pass  # Реализуйте эту функцию, если нужно

    def setup_reports_tab(self):
        """Настройка вкладки 'Отчёты'."""
        pass  # Реализуйте эту функцию, если нужно

if __name__ == "__main__":
    root = tk.Tk()
    app = IRamaApp(root)
    root.mainloop()