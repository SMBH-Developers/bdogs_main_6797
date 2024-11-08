from loguru import logger


def close_job(job):
    async def close_job_wrapper(*args, **kwargs):
        try:
            scheduler = kwargs['scheduler']
            job_id = kwargs['job_id']
            job_result = await job(*args, **kwargs)
            
            if not job_result:
                scheduler.remove_job(job_id)
        except BaseException as e:
            logger.error(f'Error closing job {job_id}: {e}')
        
        return job_result
    
    return close_job_wrapper
