import pickle
import pytest
from src.tasks.ping.ping import chain_ping, ping
from src.tasks.ping.utill import (
    is_last_message_time,
    send_ping
)
from src.models import db
from src.tasks.ping.utill import PingText

@pytest.mark.usefixtures('add_user', 'scheduler')
class TestPing:
    
    # async def test_is_last_message_time(self, get_client, user_id, message):
    #     assert await is_last_message_time(
    #         client=get_client,
    #         user_id=user_id,
    #         message=message
    #     )

    # async def test_send_ping(self, get_client, user_id, ping_step):
    #     '''Изменит последнее отправленное сообщение в классе клиента'''
    #     old_message_time = get_client.message.date
    #     result_message = await send_ping(
    #         client=get_client,
    #         user_id=user_id,
    #         ping_step=ping_step
    #     )
    #     assert result_message is not None
    #     assert result_message.text == PingText[ping_step].value.format(name=None)
    #     assert result_message.date > old_message_time
        
    async def test_ping(
        self,
        get_client,
        user_id,
        job_time,
        job_id,
        redis_client
    ):
        '''Создаст задачу в schedule'''
        job_id = await ping(
            client=get_client,
            user_id=user_id,
            message=get_client.message,
            job_time=job_time
        )
        
        assert job_id is not None
        ping_step = await db.get_ping_step(user_id)
        assert ping_step == 'FIRST'
        assert await redis_client.hget('dispatched_trips_jobs',job_id) # if ok returns bytes else None
        
    # async def test_chain_ping(
    #     self,
    #     get_client,
    #     user_id,
    #     job_id,
    #     redis_client
    # ):
    #     '''Изменит последнее отправленное сообщение в классе клиента так как будет вызов send_ping'''
    #     result_message = await chain_ping(
    #         user_id=user_id,
    #         client=get_client,
    #         message=get_client.message,
    #         job_id=job_id
    #     )
    #     assert result_message is not None
    #     redis_job = await redis_client.hget('dispatched_trips_jobs',job_id)
    #     assert redis_job is not None
        
    #     # так как декоратор close_job меняет kwargs message, то проверяем обновленное сообщение
    #     job_state = pickle.loads(redis_job)
    #     assert job_state['kwargs']['message'] == result_message
        
    #     ping_step = await db.get_ping_step(user_id)
    #     assert ping_step == 'SECOND'

    async def test_remove_job_in_close_job(
        self,
        user_id,
        job_id,
        redis_client,
        get_client,
        
    ):
        await db.set_ping_step(user_id, 'THIRD')
        assert not await chain_ping(
            user_id=user_id,
            client=get_client,
            message=get_client.message,
            job_id=job_id
        )
        assert await redis_client.hget('dispatched_trips_jobs',job_id) is None
        
        ping_step = await db.get_ping_step(user_id)
        assert ping_step is None
