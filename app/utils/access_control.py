from app.database import is_admin, get_user_chats
from app.models.user import User

async def check_access_rights(requester_id: int, target_user: str):
    """Проверяет права доступа пользователя к истории другого пользователя."""
    
    # Проверяем, является ли запрашивающий администратором
    if await is_admin(requester_id):
        return True
    
    # Получаем объекты пользователей
    requester = await User.get(requester_id)
    target = await User.get_by_username(target_user)
    
    if not target:
        return False  # Целевой пользователь не существует
    
    # Пользователь может просматривать свою историю
    if requester.id == target.id:
        return True
    
    # Проверяем, является ли запрашивающий владельцем чата, в котором есть целевой пользователь
    requester_owned_chats = await get_user_chats(requester.id, is_owner=True)
    target_chats = await get_user_chats(target.id)
    
    for chat in requester_owned_chats:
        if chat in target_chats:
            return True
    
    return False
