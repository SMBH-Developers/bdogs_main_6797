from loguru import logger
from apscheduler.jobstores.base import JobLookupError


def close_job(job):
    async def close_job_wrapper(*args, **kwargs):
        try:
            scheduler = kwargs['scheduler']
            job_id = kwargs['job_id']
            job_result = await job(*args, **kwargs)
            if job_result:
                current_job = scheduler.get_job(job_id, 'default')
                if current_job:
                    current_kwargs = current_job.kwargs
                    current_kwargs['message'] = job_result
                    
                    scheduler.modify_job(
                        current_job,
                        kwargs=current_kwargs,
                    )
            else:
                scheduler.remove_job(job_id, 'default')
        except JobLookupError as e:
            logger.warning(f'Job {job_id} not found: {e}')
        except Exception as e:
            logger.error(f'Unexpected error closing job {job_id}: {e}')
        
        return job_result
    
    return close_job_wrapper
