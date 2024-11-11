from datetime import datetime
from typing import AsyncGenerator

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
    text: str = ''
    
@dataclass
class MockDialog:
    read_outbox_max_id: int

@dataclass
class MockClient:
    message: MockMessage
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def get_chat_history(self, user_id, limit=1) -> AsyncGenerator[MockMessage, None]:
        try:
            yield self.message
        except Exception as e:
            logger.error(f'Error getting chat history for user {user_id}: {e}')
            
    async def send_message(self, user_id, text) -> MockMessage:
        self.message = MockMessage(
            chat=MockChat(id=user_id),
            id=self.message.id + 1,
            date=datetime.now(),
            text=text
        )
        return self.message
    
    async def resolve_peer(self, user_id):
        return MockChat(id=user_id)
    
    async def invoke(self, *args, **kwargs):
        return [MockDialog(read_outbox_max_id=self.message.id + 1)]
