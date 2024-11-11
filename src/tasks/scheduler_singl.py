from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from src.config import settings
from threading import Lock


class Singleton:
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    
    
class SchedulerSingleton(Singleton, AsyncIOScheduler):
    
    def __init__(self, **kwargs):
        print(settings.MODE)
        if not hasattr(self, '_initialized') or not self._initialized:
            print(settings.MODE)
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
            self._initialized = True
