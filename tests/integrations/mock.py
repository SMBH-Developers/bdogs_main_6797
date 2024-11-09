from datetime import datetime


from dataclasses import dataclass

from loguru import logger


@dataclass
class MockChat:
    id: int

@dataclass
class MockMessage:
    chat: MockChat
    id: int
    date: datetime
    outgoing: bool = True

@dataclass(frozen=True)
class MockClient:
    date: datetime
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def get_chat_history(self, user_id, limit=1):
        try:
            yield MockMessage(
                chat=MockChat(id=user_id),
                id=1,
                date=self.date,
                outgoing=True
            )
        except Exception as e:
            logger.error(f'Error getting chat history for user {user_id}: {e}')
            
    async def send_message(self, user_id, text):
        pass
