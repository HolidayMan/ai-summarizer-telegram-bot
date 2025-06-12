from app.external_services.postgresql import PostgreSQL
from app.settings import get_settings


class ExternalServices:
    config = get_settings()

    database = PostgreSQL(
        username=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        database=config.POSTGRES_DB,
        echo_pool=config.POSTGRES_ECHO_POOL,
        pool_size=config.POSTGRES_POOL_SIZE,
        connection_retry_period_sec=config.POSTGRES_CONNECTION_RETRY_PERIOD_SEC,
    )
