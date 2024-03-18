from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "SECRET_KEY"
    algorithm: str = "HS256"

    db_user: str = "DB_USER"
    db_password: str = "DB_PASSWORD"
    db: str = "DB"
    db_host: str = "DB_HOST"
    db_port: int = 5433

    redis_host: str = "REDIS_HOST"
    redis_port: int = 6379
    redis_password: str = "REDIS_PASSWORD"

    mail_username: str = "HERO@meta.ua"
    mail_password: str = "HERO_MAILBOX_PASSWORD"
    mail_from: str = "HERO@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


config = Settings()
