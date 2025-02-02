from functools import wraps
from loguru import logger
from apscheduler.jobstores.base import JobLookupError

from src.tasks.scheduler_singl import SchedulerSingleton

def close_job(job):
    @wraps(job)
    async def close_job_wrapper(*args, **kwargs):
        try:
            job_id = kwargs['job_id']
        except KeyError:
            logger.error('Job ID not found in kwargs, old job will be removed')
            return
        try:
            scheduler = SchedulerSingleton()
            job_result = await job(*args, **kwargs)
            if job_result:
                current_job = scheduler.get_job(job_id, 'default')
                if current_job and job_result != 'SKIP':
                    current_kwargs = current_job.kwargs
                    current_kwargs['message'] = job_result
                    scheduler.modify_job(
                        job_id,
                        kwargs=current_kwargs,
                    )
            else:
                scheduler.remove_job(job_id, 'default')
                logger.info(f'Job {job_id} removed')
                return
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            scheduler.remove_job(job_id, 'default')
            return
        
        return job_result
    
    return close_job_wrapper
