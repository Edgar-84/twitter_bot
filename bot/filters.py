"""This module contains custom created filters: IsAdminProgramState, NewChatMembersFilter, IsSuperAdmin"""
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
# from aiogram.fsm.context import FSMContext
# from aiogram.filters.command import Command
# from bot.main import bot
from db.facade import DB
# from aiogram.types import ChatMemberUpdated


class RegisteredUser(Filter):
    async def __call__(self, message: Message):
        user = await DB.user_crud.read(id_=message.from_user.id)
        if user:
            return True
        return False

class NotRegisteredUser(Filter):
    async def __call__(self, message: Message):
        user = await DB.user_crud.read(id_=message.from_user.id)
        if user:
            return False
        return True

class CancelButton(Filter):
    async def __call__(self, call: CallbackQuery):
        return call.data == "cancel"

class ProceedToWorkout(Filter):
    async def __call__(self, call: CallbackQuery):
        return call.data == "proceed_to_workout"