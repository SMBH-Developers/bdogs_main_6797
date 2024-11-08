from src.tasks.ping.ping import chain_ping, ping
from src.tasks.ping.utill import (
    is_last_message_time,
    is_last_message_time_read,
    send_ping
)

class TestPing:
    jobs = {'ping_1234567890': 'ping_1234567890'}
    
    
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
        
    async def test_ping(self, client, user_id, message, scheduler, job_time):
        job_id = await ping(
            client=client,
            user_id=user_id,
            message=message,
            scheduler=scheduler,
            job_time=job_time
        )
        assert job_id is not None
        assert job_id in self.jobs
        
    async def test_chain_ping(self, client, user_id, message, scheduler):
        job_id = self.jobs['ping_1234567890']
        
        assert await chain_ping(
            user_id=user_id,
            client=client,
            message=message,
            scheduler=scheduler,
            job_id=job_id
        )
