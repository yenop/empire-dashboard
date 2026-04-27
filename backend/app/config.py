from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "appempire"
    db_user: str = "appempire"
    db_password: str = "change_me"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio_secret_change"
    minio_bucket: str = "empire"
    minio_secure: bool = False

    empire_auth_username: str = "admin"
    empire_password_hash: str = ""
    empire_jwt_secret: str = "dev-only-change-in-production-min-32-chars!!"
    empire_jwt_expire_minutes: int = 15

    openclaw_gateway_url: str = ""
    openclaw_gateway_token: str = ""
    openclaw_dir: str = "/openclaw-data"
    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
