from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Any

class Settings(BaseSettings):
    MODE: Literal['TEST', 'PROD'] = Field(default='TEST') # TEST or PROD
    name: str
    api_id: int
    api_hash: str
    phone_number: str
    GOOGLE_CREDS: dict[str, Any]

    postgres_dsn: PostgresDsn

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # Redis
    REDIS_HOST_NAME: str = Field(default='redis')
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default='')
    REDIS_JOB_DATABASES: int = Field(default=0) # 0 - default, by apscheduler
    REDIS_JOB_DATABASES_TEST: int = Field(default=1) # 1 - test
    
    @property
    def redis_uri(self) -> str:
        return f'redis://{self.REDIS_HOST_NAME}:6379'


settings = Settings()
