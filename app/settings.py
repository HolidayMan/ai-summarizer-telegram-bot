from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "telegram_bot"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_ECHO_POOL: bool = False
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_CONNECTION_RETRY_PERIOD_SEC: int = 5


    @property
    def POSTGRES_URL(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )

    OPENAI_API_ENDPOINT: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_SUMMARY_TIME: str = "20:00"
    TIMEZONE: str = "UTC"


def get_settings(env_file: str = ".env") -> Settings:
    return Settings(_env_file=env_file)
