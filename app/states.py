from aiogram.fsm.state import State, StatesGroup


class DesignRequestStates(StatesGroup):
    waiting_project_name = State()
    waiting_what_to_design = State()
    waiting_project_info = State()
    waiting_email = State()
    waiting_for_file = State()
    waiting_contact = State()


class Newsletter(StatesGroup):
    message = State()