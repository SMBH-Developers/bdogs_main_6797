from apscheduler.schedulers.asyncio import AsyncIOScheduler

class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    
class SchedulerSingleton(Singleton, AsyncIOScheduler):
    pass