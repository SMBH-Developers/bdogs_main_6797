from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    name: str
    api_id: int
    api_hash: str
    phone_number: str

    postgres_dsn: PostgresDsn

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # Redis
    REDIS_HOST_NAME: str = Field(default='localhost')
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default='')
    REDIS_JOB_DATABASES: int = Field(default=0) # 0 - default, by apscheduler


settings = Settings()
