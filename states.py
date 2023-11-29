from aiogram.fsm.state import StatesGroup, State


class StartState(StatesGroup):
    start_state = State()


class CreateUser(StatesGroup):
    input_needed_hours = State()
    input_needed_date = State()


class CompleteTask(StatesGroup):
    input_project = State()
    input_name = State()
    input_hours = State()
    input_comment = State()


class CheckStats(StatesGroup):
    check_stats = State()


class CheckTasks(StatesGroup):
    check_tasks = State()


class AddProject(StatesGroup):
    add_project = State()


class ChangeTaskInfo(StatesGroup):
    change_task_info = State()
    change_hours = State()
    input_new_hours = State()
