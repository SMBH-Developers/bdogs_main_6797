from enum import Enum
from typing import Optional

class PingText(Enum):
    FIRST = 'Простите, {name}, не дождалась от вас ответа, вы заняты?🙌'
    SECOND = "Я понимаю, что все мы заняты, но я по-настоящему верю, что наше общение может принести пользу. Есть ли шанс услышать вас сегодня?🙏😊"
    THIRD = "{name}, возможно, вам удобнее пообщаться в другое время?😊 Подскажите, когда вам будет удобно?❤️"

    @classmethod
    def get_next_step(cls, step: str) -> Optional[str]:
        if step == 'THIRD':
            return None
        steps = list(PingText)  # Получаем список всех значений enum
        try:
            current_step = PingText[step]  # Получаем текущий шаг
            current_index = steps.index(current_step)
            return steps[current_index + 1].name  # Возвращаем имя следующего шага
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def paginate(cls, ping_step: str, name: str) -> str:
        text = cls[ping_step].value
        if not name:
            text = text.replace('{name}, ', '')
        else:
            text = text.format(name=name)
        return text