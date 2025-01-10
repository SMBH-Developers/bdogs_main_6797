from src.config.scheduler_singl import SchedulerSingleton
from src.config import settings
import pickle
import redis
from loguru import logger

# Маппинг старых путей на новые
PATH_MAPPING = {
    'src.tasks.ping.ping:chain_ping': 'version.v2.tasks.ping.ping:chain_ping',
    # Добавьте другие пути по необходимости
}

async def migrate_scheduler_jobs():
    """Миграция путей для существующих задач APScheduler в Redis"""
    try:
        # Подключаемся к Redis напрямую для работы с сырыми данными
        redis_client = redis.Redis(
            host=settings.REDIS_HOST_NAME,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_JOB_DATABASES if settings.MODE == 'PROD' else settings.REDIS_JOB_DATABASES_TEST
        )

        # Получаем все задачи
        jobs = redis_client.hgetall('dispatched_trips_jobs')
        
        if not jobs:
            logger.warning("No jobs found in Redis")
            return

        updated_count = 0
        failed_count = 0

        for job_id, job_state in jobs.items():
            try:
                # Десериализуем состояние задачи
                state = pickle.loads(job_state)
                
                old_path = state.get('func_ref')
                if old_path in PATH_MAPPING:
                    # Обновляем путь
                    state['func_ref'] = PATH_MAPPING[old_path]
                    
                    # Сохраняем обновленное состояние
                    redis_client.hset(
                        'dispatched_trips_jobs',
                        job_id,
                        pickle.dumps(state)
                    )
                    updated_count += 1
                    logger.info(f"Updated job {job_id.decode()}: {old_path} -> {state['func_ref']}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to update job {job_id}: {str(e)}")
                continue

        logger.info(f"Migration completed. Updated: {updated_count}, Failed: {failed_count}")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        redis_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_scheduler_jobs()) 