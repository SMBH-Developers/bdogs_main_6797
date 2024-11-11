from functools import wraps
from loguru import logger
from apscheduler.jobstores.base import JobLookupError

from src.tasks.scheduler_singl import SchedulerSingleton

def close_job(job):
    @wraps(job)
    async def close_job_wrapper(*args, **kwargs):
        try:
            scheduler = SchedulerSingleton()
            job_id = kwargs['job_id']
            job_result = await job(*args, **kwargs)
            if job_result:
                current_job = scheduler.get_job(job_id, 'default')
                logger.info(f'Job {current_job} found')
                if current_job:
                    current_kwargs = current_job.kwargs
                    logger.info(f'Current kwargs: {current_kwargs}')
                    current_kwargs['message'] = job_result
                    logger.info(f'Current kwargs after update: {current_kwargs}')
                    
                    scheduler.modify_job(
                        current_job,
                        kwargs=current_kwargs,
                    )
            else:
                scheduler.remove_job(job_id, 'default')
                logger.info(f'Job {job_id} removed')
        except Exception as e:
            logger.error(f'Unexpected error closing job {job_id}: {e}')
        
        return job_result
    
    return close_job_wrapper
