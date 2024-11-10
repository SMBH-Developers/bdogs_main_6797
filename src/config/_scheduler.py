from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from src.tasks.scheduler_singl import SchedulerSingleton
from ._settings import settings

jobstores = {
    'default': RedisJobStore(
        jobs_key='dispatched_trips_jobs',
        run_times_key='dispatched_trips_running',
        host=settings.REDIS_HOST_NAME,
        db=settings.REDIS_JOB_DATABASES,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD
        )
    }
executors = {
    'default': AsyncIOExecutor(),
    'processpool': ProcessPoolExecutor(3)
}
scheduler = SchedulerSingleton({'apscheduler.timezone': 'Europe/Moscow'}) # ,jobstores=jobstores, executors=executors