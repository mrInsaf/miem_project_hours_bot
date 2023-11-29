import asyncio
import logging
import sqlite3
import math
import sys
import datetime
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.send_message import SendMessage

from states import *
from db import *
from date_works import *
from user import User

TOKEN = '6909420020:AAH69WzzAiYgfKYpXN-rjRP2zYtKQFYTNPk'

dp = Dispatcher()

user = User()


def create_kb():
    kb = InlineKeyboardBuilder()
    cancel_button = InlineKeyboardButton(text="Назад", callback_data=f'back')
    kb.add(cancel_button)
    return kb



@dp.callback_query(CreateUser.input_needed_hours, F.data == "back")
@dp.callback_query(CompleteTask.input_project, F.data == "back")
@dp.callback_query(CheckStats.check_stats, F.data == "back")
@dp.callback_query(CheckTasks.check_tasks, F.data == "back")
@dp.callback_query(AddProject.add_project, F.data == "back")
@dp.callback_query(ChangeTaskInfo.change_task_info, F.data == "back")
async def start_command(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StartState.start_state)
    user_data = get_user_data(callback.from_user.id)
    user.set_all_fields(*user_data)
    kb = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="Зачесть задачу", callback_data="complete task"),
        InlineKeyboardButton(text="Просмотреть завершенные задачи", callback_data="check tasks"),
        InlineKeyboardButton(text="Посмотреть статистику", callback_data="check stats"),
        InlineKeyboardButton(text="Добавить проект", callback_data="add project"),
        InlineKeyboardButton(text="Изменить информацию о задачах", callback_data="change task info"),
    ]
    for button in buttons:
        kb.add(button)
    kb.adjust(1)

    await callback.message.answer(text="Здарова нахрен. Выберите действие:", reply_markup=kb.as_markup())


@dp.message(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(StartState.start_state)
    if check_user_in_db(message.from_user.id):
        user_data = get_user_data(message.from_user.id)
        user.set_all_fields(*user_data)
        kb = InlineKeyboardBuilder()
        buttons = [
            InlineKeyboardButton(text="Зачесть задачу", callback_data="complete task"),
            InlineKeyboardButton(text="Просмотреть завершенные задачи", callback_data="check tasks"),
            InlineKeyboardButton(text="Посмотреть статистику", callback_data="check stats"),
            InlineKeyboardButton(text="Добавить проект", callback_data="add project"),
            InlineKeyboardButton(text="Изменить информацию о задачах", callback_data="change task info"),
        ]
        for button in buttons:
            kb.add(button)
        kb.adjust(1)

        await message.answer(text="Здарова нахрен. Выберите действие:", reply_markup=kb.as_markup())
    else:
        await message.answer("Здарова нахрен, я помогу тебе закрыть проектные кредиты к нужному времени")
        await message.answer("Введи количество часов, которые необходимо заработать")
        await state.set_state(CreateUser.input_needed_hours)


@dp.message(CreateUser.input_needed_hours)
async def input_needed_hours(message: Message, state: FSMContext):
    try:
        needed_hours = int(message.text)
        await state.update_data(needed_hours=needed_hours)
        await message.answer(
            "Отлично, теперь введите желаемую дату, к которой необходимо накопить часы")
        await state.set_state(CreateUser.input_needed_date)
    except Exception:
        await message.answer("Введите, пожалуйста, целое число")


@dp.message(CreateUser.input_needed_date)
async def input_needed_date(message: Message, state: FSMContext):
    input_date = message.text
    try:
        current_date = datetime.now().strftime('%d.%m.%Y')
        # Парсим введенную дату
        date_object = datetime.strptime(input_date, "%d.%m.%Y")
        # Форматируем дату обратно в строку
        formatted_date = date_object.strftime("%d.%m.%Y")
        data = await state.get_data()
        needed_hours = data['needed_hours']
        hours_per_day = math.ceil(needed_hours / count_weekdays(formatted_date))
        corrected_date = correct_date(needed_hours, hours_per_day)
        user_data = [message.from_user.first_name, needed_hours, formatted_date, needed_hours, hours_per_day, corrected_date, current_date]
        create_user(message.from_user.id, user_data)
        await message.answer(text=f"Отлично, вы добавили цель. "
                                  f"В вашем случае надо работать {hours_per_day} часов в день, таким образом вы "
                                  f"достигните цели к {corrected_date}")
        await start_command(message, state)
    except ValueError:
        await message.answer("Некорректный формат даты. Введите дату в формате дд.мм.гггг")


@dp.callback_query(F.data == "complete task")
async def input_project_name(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    projects = select_projects_of(callback.from_user.id)
    for project in projects:
        kb.add(InlineKeyboardButton(text=f'{project[1]}', callback_data=f"selected project_id:{project[0]}"))
    kb.adjust(1)
    await callback.message.answer(text="Выберите название проекта", reply_markup=kb.as_markup())
    await state.set_state(CompleteTask.input_project)


@dp.callback_query(CompleteTask.input_name, F.data == "back")
async def back_to_input_project_name(callback: CallbackQuery, state: FSMContext):
    await input_project_name(callback, state)


@dp.callback_query(CompleteTask.input_project)
async def input_task_name(callback: CallbackQuery, state: FSMContext):
    project_id = callback.data.split(':')[1]
    print(project_id)
    await state.update_data(project_id=project_id)
    kb = create_kb()
    await callback.message.answer(text="Введите название задачи", reply_markup=kb.as_markup())
    await state.set_state(CompleteTask.input_name)


@dp.callback_query(CompleteTask.input_hours, F.data == "back")
async def back_to_input_task_name(callback: CallbackQuery, state: FSMContext):
    await input_task_name(callback, state)


@dp.message(CompleteTask.input_name)
async def input_hours(message: Message, state: FSMContext):
    kb = create_kb()
    await state.update_data(name=message.text)
    await message.answer(text="Введите количество часов за эту задачу", reply_markup=kb.as_markup())
    await state.set_state(CompleteTask.input_hours)


@dp.callback_query(CompleteTask.input_comment)
async def back_to_input_hours(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text="Введите количество часов за эту задачу", reply_markup=kb.as_markup())
    await state.set_state(CompleteTask.input_hours)


@dp.message(CompleteTask.input_hours)
async def input_comment(message: Message, state: FSMContext):
    kb = create_kb()
    try:
        hours = int(message.text)
        await state.update_data(hours=hours)
        await message.answer(text="Введите комментарий к этой задаче. Если комментария нет, введите '0'",
                             reply_markup=kb.as_markup())
        await state.set_state(CompleteTask.input_comment)
    except Exception:
        await message.answer(text="Пожалуйста, введите число")


@dp.message(CompleteTask.input_comment)
async def process_task(message: Message, state: FSMContext):
    comment = message.text
    if comment == "0":
        comment = ''
    data = await state.get_data()
    task_data = [data['name'], data['hours'], comment, data['project_id']]
    insert_task(task_data, message.from_user.id, user)
    await message.answer(text="Отлично, вы добавили задачу")
    await start_command(message, state)


@dp.callback_query(F.data == "check stats")
async def check_stats(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    user_data = vars(user)
    current_date = datetime.now().strftime('%d.%m.%Y')
    user_id = user_data['user_id']
    total_hours = user_data['total_hours']
    hours_remaining = user_data['hours_remaining']
    date_of_finish = user_data['date_of_finish']
    hours_per_day = user_data['hours_per_day']
    corrected_date = user_data['corrected_date']
    tasks_completed, hours = count_task_and_hours(user_id)
    today_hours = select_today_hours(user_id)
    total_lag = calculate_total_lag(user, hours)
    lag_str = ''
    if total_lag == 0:
        lag_str = 'не отстаете от графика, отлично!'
    elif total_lag > hours_per_day:
        lag_str = f'отстаете от графика на {total_lag} часов это больше, чем надо заработать за день({hours_per_day})'
    elif total_lag > 0:
        lag_str = f'отстаете от графика на {total_lag} часов'
    elif total_lag < 0:
        lag_str = f'опережаете график на {-total_lag} часов, невероятно!'

    await callback.message.answer(text=f"Ваша задача набрать {total_hours} часов до {date_of_finish}. \n\n"
                                       f"Работая по {hours_per_day} часов в день, вы достигните цели к {corrected_date}\n\n"
                                       f"Количество завершенных задач: {tasks_completed}\nКоличество накопленных часов: {hours}\n\n"
                                       f"Осталось накопить: {hours_remaining} часов\n\n"
                                       f"За сегодня вы накопили {today_hours} часов из {hours_per_day}\n"
                                       f"На данный момент вы {lag_str}", reply_markup=kb.as_markup())
    await state.set_state(CheckStats.check_stats)
    print(user)


@dp.callback_query(F.data == "change task info")
async def change_task_info(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    buttons = [
        InlineKeyboardButton(text="Изменить часы за задачу", callback_data='correct hours'),
        InlineKeyboardButton(text="Изменить комментарий задачи", callback_data='correct comment'),
        InlineKeyboardButton(text="Удалить задачу", callback_data='delete task')
    ]
    for button in buttons:
        kb.add(button)
    kb.adjust(1)
    await callback.message.answer(text="Выберите дейстие", reply_markup=kb.as_markup())
    await state.update_data(users_tasks=select_tasks(callback.from_user.id))
    await state.set_state(ChangeTaskInfo.change_task_info)


@dp.callback_query(ChangeTaskInfo.change_task_info, F.data == "correct hours")
async def correct_hours(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer(text=f'Введите id задачи, которую надо отредактировать\n\n {data["users_tasks"][1]}')
    await state.set_state(ChangeTaskInfo.change_hours)


@dp.message(ChangeTaskInfo.change_hours)
async def change_hours(message: Message, state: FSMContext):
    data = await state.get_data()
    ids = [task_data[0] for task_data in data["users_tasks"][0]]
    try:
        input_id = int(message.text)
        if input_id not in ids:
            await message.answer(text="Вы ввели неправильный id, попробуйте еще раз")
        else:
            await state.update_data(task_id=input_id)
            await message.answer(text="Введите новое количество часов для этой задачи")
            await state.set_state(ChangeTaskInfo.input_new_hours)
    except Exception:
        await message.answer(text="Введите число")


@dp.message(ChangeTaskInfo.input_new_hours)
async def process_change_hours(message: Message, state: FSMContext):
    try:
        new_hours = int(message.text)
        data = await state.get_data()
        task_id = data['task_id']
        update_hours(task_id, new_hours, user)
        await message.answer(text="Отлично, вы изменили количество часов для этой задачи, нажмите /start")
    except Exception:
        await message.answer(text="Введите целое количество часов")


@dp.callback_query(ChangeTaskInfo.change_task_info, F.data == "delete task")
async def delete_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=f'Введите id задачи, которую надо удалить\n\n {select_tasks(callback.from_user.id)}')


@dp.callback_query(F.data == "check tasks")
async def check_task_info(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text=f"Вот ваши выполненные задачи:\n\n{select_tasks(callback.from_user.id)[1]}",
                                  reply_markup=kb.as_markup())
    await state.set_state(CheckTasks.check_tasks)


@dp.callback_query(F.data == "add project")
async def add_project(callback: CallbackQuery, state: FSMContext):
    kb = create_kb()
    await callback.message.answer(text="Напишите название проекта, который хотите добавить", reply_markup=kb.as_markup())
    await state.set_state(AddProject.add_project)


@dp.message(AddProject.add_project)
async def process_adding_project(message: Message, state: FSMContext):
    project_info = [message.text, message.from_user.id]
    add_project_to_db(project_info)
    await message.answer(text=f"Проект {message.text} добавлен")
    await start_command(message, state)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
