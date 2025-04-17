import asyncio
from db.models.user import UserCRUD, UserRequestCRUD
from db.models.profile import ProfileCRUD
from db.models.friend import FriendCRUD

class DB:
    user_crud = UserCRUD()
    user_request_crud = UserRequestCRUD()
    profile_crud = ProfileCRUD()
    friend_crud = FriendCRUD()
