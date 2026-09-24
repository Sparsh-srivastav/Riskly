from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Riskly"
    app_env: str = "development"

    database_url: str = "postgresql://riskly:password@localhost:5432/riskly"

    jwt_secret: str = "change_this_later"

    kafka_bootstrap_servers: str = "localhost:9092"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()