from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from src.config import settings


class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    
class SchedulerSingleton(Singleton, AsyncIOScheduler):
    
    def __init__(self, **kwargs):
        jobstores = {
            'default': RedisJobStore(
                jobs_key='dispatched_trips_jobs',
                run_times_key='dispatched_trips_running',
                host=settings.REDIS_HOST_NAME,
                db=settings.REDIS_JOB_DATABASES_TEST if settings.MODE == 'TEST' else settings.REDIS_JOB_DATABASES,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD
            )
        }
        executors = {
            'default': AsyncIOExecutor(),
            'processpool': ProcessPoolExecutor(3)
        }
        super().__init__(
            {'apscheduler.timezone': 'Europe/Moscow'},
            jobstores=jobstores,
            executors=executors,
            **kwargs
        )
