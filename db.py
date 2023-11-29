import sqlite3
from datetime import datetime
from user import User

conn = sqlite3.connect('miem_hours.db')
cursor = conn.cursor()
from date_works import *


def select(query):
    query = query
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.commit()
    return rows


def insert(table_name, data_list, auto_increment_id):
    # Получаем информацию о столбцах в таблице
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    columns = columns[auto_increment_id:]
    print(columns)

    # Генерируем SQL-запрос для вставки данных
    placeholders = ', '.join(['?'] * len(columns))
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    # Вставляем данные в таблицу
    cursor.execute(query, data_list)
    conn.commit()

    # Закрываем соединение с базой данных
    conn.close()


def insert_task(task_data: list, user_id, user: User):
    hours = task_data[1]
    hr = hours_remaining(user_id) - hours
    dttm = datetime.now().strftime("%d.%m.%Y")
    task_data.append(dttm)
    task_data.append(user_id)
    query = ('insert into completed_tasks (name, hours, comment, project_id, date_added, user_id) '
             'values (?, ?, ?, ?, ?, ?)')
    cursor.execute(query, task_data)
    conn.commit()
    select(f'UPDATE users SET hours_remaining = {hr} WHERE user_id = {user_id}')
    user.hours_remaining = hr


def hours_remaining(user_id):
    return select(f'select hours_remaining from users where user_id = {user_id}')[0][0]


def create_user(user_id, user_data: list):
    user_data.insert(0, user_id)
    query = (f'insert into users (user_id, name, total_hours, date_of_finish, hours_remaining, hours_per_day, '
             f'corrected_date, registration_date)'
             f'values (?, ?, ?, ?, ?, ?, ?, ?)')
    cursor.execute(query, user_data)
    conn.commit()


def check_user_in_db(user_id):
    if select(f'select * from users where user_id = {user_id}'):
        return True
    else:
        return False


def get_user_data(user_id: int):
    return select(f'select * from users where user_id = {user_id}')[0]


def input_hours_per_day(hours: list):
    query = f'insert into users (hours_per_day) values (?)'
    cursor.execute(query, hours)
    conn.commit()


def count_task_and_hours(user_id: int):
    return select(f'select count(1), sum(hours) from completed_tasks where user_id = {user_id}')[0]


def select_tasks(user_id: int):
    result_str = ''
    tasks = select(f'select id, ct.name, p.name, hours, comment, date_added from completed_tasks ct join projects p on '
                   f'ct.project_id = p.project_id where ct.user_id = {user_id}')
    for task in tasks:
        result_str += (f'id: {task[0]}\nНазвание: {task[1]}\nПроект: {task[2]}\nКоличество часов: {task[3]}\nКомментарий: {task[4]}\n'
                       f'Время добавления: {task[5]}\n')
        result_str += "\n"
    return [tasks, result_str]


def select_today_hours(user_id: int):
    current_date = datetime.now().strftime('%d.%m.%Y')
    return select(f'SELECT sum(hours) FROM completed_tasks WHERE user_id = {user_id} and date_added = "{current_date}"')[0][0]
    

def add_project_to_db(project_info: list):
    query = f'insert into projects (name, user_id) values (?, ?)'
    cursor.execute(query, project_info)
    conn.commit()


def select_projects_of(user_id: int):
    return select(f'select project_id, name from projects where user_id = {user_id}')


def update_hours(task_id: int, new_hours: int, user: User):
    select(f'UPDATE completed_tasks SET hours = {new_hours} WHERE id = {task_id}')
    count_hours = count_task_and_hours(user.user_id)[1]
    new_hr = user.total_hours - count_hours
    user.hours_remaining = new_hr

    select(f'UPDATE users SET hours_remaining = {new_hr} WHERE user_id = {user.user_id}')
    print(user)



def select_tasks_html(user_id: int):
    result_str = ''
    tasks = select(f'select * from completed_tasks where user_id = {user_id}')
    for task in tasks:
        result_str += (f'<p>id: {task[0]}</p><p>Название: {task[1]}</p><p>Количество часов: {task[2]}</p><p>Комментарий: {task[3]}</p>'
                       f'<p>Время добавления: {task[5]}</p>')
        result_str += "<br>"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Пример HTML-файла</title>
    </head>
    <body>
        {result_str}
    </body>
    </html>
    """

    # Задаем имя файла
    file_name = "tasks.html"

    # Открываем файл на запись и записываем в него HTML-код
    with open(file_name, "w") as file:
        file.write(html_content)

    print(f"HTML-файл '{file_name}' успешно создан.")


