from datetime import datetime
from version.v1.schemas.users import OutputUser
from src.logic.telegram.tasks_mexin.statistics import StatisticsMexinInterface

class StatisticsMexin(StatisticsMexinInterface):
        
    async def _get_users_and_dialogs(self, users_with_folder: list[OutputUser]):
        dialogs = [dialog async for dialog in self.client.get_dialogs(limit=1500)]

        users_with_folder_dict = {user.id: user.folder for user in users_with_folder}

        relevant_dialogs = []
        for dialog in dialogs:
            if dialog.chat.id in users_with_folder_dict:
                messages = self.client.get_chat_history(dialog.chat.id)
                messages = [message async for message in messages]
                if messages and messages[-1].date.date() == datetime.now().date():
                    relevant_dialogs.append(dialog.chat.id)

        return users_with_folder_dict, relevant_dialogs

    async def get_folder_stats_today(self, users_with_folder: list[OutputUser]):
        users_with_folder_dict, relevant_dialogs = await self._get_users_and_dialogs(users_with_folder)
        folder_counts = {"Нет папки": 0}

        for user_id in relevant_dialogs:
            folder = users_with_folder_dict.get(user_id)
            if folder is None:
                folder_counts["Нет папки"] += 1
            else:
                if folder in folder_counts:
                    folder_counts[folder] += 1
                else:
                    folder_counts[folder] = 1

        # Формирование результата
        result = ""
        result += "Сегодня Су: {}\n".format(folder_counts.get("Су", 0))
        result += "Сегодня Ек2: {}\n".format(folder_counts.get("Ек2", 0))
        result += "Сегодня Ан: {}\n".format(folder_counts.get("Ан", 0))
        result += "Сегодня Та: {}\n".format(folder_counts.get("Та", 0))
        result += "Сегодня Ве: {}\n\n".format(folder_counts.get("Ве", 0))

        total_in_folders = sum(folder_counts.values()) - folder_counts["Нет папки"]
        result += "Всего в папках: {}\n\n".format(total_in_folders)

        result += "Пользователей без папки: {}\n\n".format(folder_counts["Нет папки"])

        count = sum(value for value in folder_counts.values())
        result += "Всего за сегодня: {}".format(count)

        return result