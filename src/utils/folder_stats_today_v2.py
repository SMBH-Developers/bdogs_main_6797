from typing import Dict, List, Tuple, Set
from datetime import datetime
from loguru import logger
import asyncio

from src.config import client
from src.models import async_session, User

from sqlalchemy import select, update, and_


async def get_users():
    async with async_session() as session:
        users = (
            await session.execute(
                select(User.id, User.folder)
                .where(User.registration_date >= datetime.now().replace(hour=00, minute=00, second=00, microsecond=00))
            )
        ).all()
    return users


async def get_users_and_dialogs() -> Tuple[Dict[int, str], List[int]]:
    """
    Получает актуальных пользователей и их диалоги.
    
    Returns:
        Tuple[Dict[int, str], List[int]]: (словарь {user_id: folder}, список активных диалогов)
    """
    try:
        # Получаем пользователей и диалоги параллельно для оптимизации
        users_with_folder, dialogs = await asyncio.gather(
            get_users(),
            get_telegram_dialogs()
        )
        
        # Создаем set для быстрого поиска
        existing_chat_ids: Set[int] = {dialog.chat.id for dialog in dialogs}
        today = datetime.now().date()
        
        # Фильтруем пользователей и находим удаленные чаты
        users_with_folder_dict: Dict[int, str] = {}
        deleted_users: List[int] = []
        
        for user_id, folder in users_with_folder:
            if user_id in existing_chat_ids:
                users_with_folder_dict[user_id] = folder
            else:
                deleted_users.append(user_id)
        
        # Очищаем папки у удаленных пользователей
        if deleted_users:
            await cleanup_deleted_users(deleted_users)

        # Получаем активные диалоги
        relevant_dialogs = await get_relevant_dialogs(
            dialogs, 
            users_with_folder_dict, 
            today
        )
        
        return users_with_folder_dict, relevant_dialogs
        
    except Exception as e:
        logger.error(f"Ошибка в get_users_and_dialogs: {str(e)}", exc_info=True)
        raise


async def get_telegram_dialogs(limit: int = 1500) -> List:
    """Получает список диалогов из Telegram."""
    return [dialog async for dialog in client.get_dialogs(limit=limit)]


async def cleanup_deleted_users(deleted_users: List[int]) -> None:
    """
    Очищает папки у удаленных пользователей.
    
    Args:
        deleted_users: Список ID удаленных пользователей
    """
        
    try:
        async with async_session() as session:
            # Добавляем проверку существования записей перед обновлением
            result = await session.execute(
                update(User)
                .where(
                    and_(
                        User.id.in_(deleted_users),
                        User.folder.isnot(None)
                    )
                )
                .values(folder=None)
                .returning(User.id)
            )
            updated_ids = result.scalars().all()
            await session.commit()
            
            logger.info(
                f"Очищены папки у {len(updated_ids)} из {len(deleted_users)} удаленных чатов. "
                f"IDs: {updated_ids}"
            )
    except Exception as e:
        logger.error(f"Ошибка при очистке удаленных пользователей: {str(e)}")
        await session.rollback()  # Откатываем транзакцию при ошибке
        raise


async def get_relevant_dialogs(
    dialogs: List,
    users_dict: Dict[int, str],
    today: datetime.date
) -> List[int]:
    """
    Получает список активных диалогов с сообщениями за сегодня.
    
    Args:
        dialogs: Список диалогов
        users_dict: Словарь пользователей с папками
        today: Текущая дата
    
    Returns:
        List[int]: Список ID активных диалогов
    """
    relevant_dialogs = []
    
    for dialog in dialogs:
        if dialog.chat.id not in users_dict:
            continue
            
        try:
            messages = await anext(client.get_chat_history(dialog.chat.id, limit=1))
            if messages and messages.date.date() == today:
                relevant_dialogs.append(dialog.chat.id)
        except StopAsyncIteration:
            continue
        except Exception as e:
            logger.error(f"Ошибка при получении истории чата {dialog.chat.id}: {str(e)}")
            continue
    
    return relevant_dialogs


async def get_folder_stats_today():
    users_with_folder_dict, relevant_dialogs = await get_users_and_dialogs()
    folder_counts = {"Нет папки": 0}
    # result_parts = {}
    
    for user_id in relevant_dialogs:
        folder = users_with_folder_dict.get(user_id)
        if folder is None:
            folder_counts["Нет папки"] += 1
        else:
            folder_counts[folder] = folder_counts.get(folder, 0) + 1
            # result_parts[folder] = f'Сегодня {folder}: {folder_counts[folder]}'
    
    # result = '\n'.join(result_parts.values()) + "\n\n"
    result = ""
    result += "Сегодня Су: {}\n".format(folder_counts.get("Су", 0))
    result += "Сегодня Ек2: {}\n".format(folder_counts.get("Ек2", 0))
    result += "Сегодня Ан: {}\n".format(folder_counts.get("Ан", 0))
    result += "Сегодня Та: {}\n".format(folder_counts.get("Та", 0))
    result += "Сегодня Ве: {}\n".format(folder_counts.get("Ве", 0))
    result += "Сегодня Да: {}\n".format(folder_counts.get("Да", 0))
    result += "Сегодня Стас: {}\n\n".format(folder_counts.get("Cтас", 0))

    total_in_folders = sum(folder_counts.values()) - folder_counts["Нет папки"]
    result += "Всего в папках: {}\n\n".format(total_in_folders)

    result += "Пользователей без папки: {}\n\n".format(folder_counts["Нет папки"])

    count = sum(value for value in folder_counts.values())
    result += "Всего за сегодня: {}".format(count)

    return result
