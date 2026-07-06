from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Config-Driven Development Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = ""

    DEFAULT_USER_ID: str = "admin"
    DEFAULT_USER_NAME: str = "管理员"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()