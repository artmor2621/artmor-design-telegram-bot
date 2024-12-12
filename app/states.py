from aiogram.fsm.state import State, StatesGroup


class DesignRequestStates(StatesGroup):
    waiting_what_to_design = State()
    waiting_project_info = State()
    waiting_email = State()
    waiting_contact = State()