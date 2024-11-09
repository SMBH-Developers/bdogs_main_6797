import pytest
from src.tasks.ping.ping import chain_ping, ping
from src.tasks.ping.utill import (
    is_last_message_time,
    is_last_message_time_read,
    send_ping
)
from src.models import db, User

@pytest.mark.usefixtures('add_user')
class TestPing:
    
    async def test_is_last_message_time(self, client, user_id, message):
        assert await is_last_message_time(
            client=client,
            user_id=user_id,
            message=message
        )

    async def test_is_last_message_time_read(self, client, message):
        assert await is_last_message_time_read(
            client=client,
            message=message
        )

    async def test_send_ping(self, client, user_id, ping_step):
        assert await send_ping(
            client=client,
            user_id=user_id,
            ping_step=ping_step
        )
        
    async def test_ping(
        self,
        client,
        user_id,
        message,
        scheduler,
        job_time,
        job_id,
        redis_client,
    ):
        job_id = await ping(
            client=client,
            user_id=user_id,
            message=message,
            scheduler=scheduler,
            job_time=job_time
        )
        
        assert job_id is not None
        assert job_id == job_id
        
        user: User = await db.get_ping_step(user_id)
        assert user.ping_step == 'FIRST'
        assert await redis_client.get(job_id)
        
    async def test_chain_ping(
        self,
        client,
        user_id,
        message,
        scheduler,
        job_id,
        redis_client
    ):
        
        assert await chain_ping(
            user_id=user_id,
            client=client,
            message=message,
            scheduler=scheduler,
            job_id=job_id
        )
        
        assert await redis_client.get(job_id) is not None
        
        user: User = await db.get_ping_step(user_id)
        assert user.ping_step == 'SECOND'

    async def test_remove_job_in_close_job(
        self,
        user_id,
        job_id,
        redis_client,
        client,
        message,
        scheduler
    ):
        await db.set_ping_step(user_id, 'THIRD')
        assert not await chain_ping(
            user_id=user_id,
            client=client,
            message=message,
            scheduler=scheduler,
            job_id=job_id
        )
        assert await redis_client.get(job_id) is None
        
        user: User = await db.get_ping_step(user_id)
        assert user.ping_step is None