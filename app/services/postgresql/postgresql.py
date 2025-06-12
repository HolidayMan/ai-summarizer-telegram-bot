import re
import socket
from contextlib import suppress
from typing import Literal
from urllib.parse import quote

from psycopg2 import errorcodes
from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.exc import DatabaseError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.services.base import BaseService
from app.services.postgresql.base_database import Database
from app.services.postgresql.exceptions import (
    DatabaseException,
    ForeignKeyNotFoundException,
    IncorrectColumnValueException,
    ObjectAlreadyExistsException,
    TableNotFoundException,
)


__all__ = ["PostgreSQL"]


SQLSTATE_TO_DB_EXCEPTION_HM = {
    errorcodes.UNIQUE_VIOLATION: ObjectAlreadyExistsException,
    errorcodes.UNDEFINED_TABLE: TableNotFoundException,
    errorcodes.FOREIGN_KEY_VIOLATION: ForeignKeyNotFoundException,
    errorcodes.STRING_DATA_RIGHT_TRUNCATION: IncorrectColumnValueException,
    errorcodes.NOT_NULL_VIOLATION: IncorrectColumnValueException,
    errorcodes.INVALID_TEXT_REPRESENTATION: IncorrectColumnValueException,
}


class SessionHandler:
    """
    Intermediate class for managing temporarily-created session and handling exceptions.
    Main purpose: avoiding code duplication
    !!! Warning: hardcoded always try to commit when errors not handled

    :param session(AsyncSession): managed session must be passed from outside

    """

    def __init__(
        self, async_session: AsyncSession = None, sync_session: Session = None
    ):  # pylint:disable=redefined-outer-name
        self._is_async = async_session is not None
        self.session = async_session or sync_session

    async def __aenter__(self) -> AsyncSession:
        assert self._is_async, "This is sync session!"
        await self.session.begin()
        return self.session

    async def __aexit__(self, exception_type: type, exception: Exception, _traceback) -> None:
        """Handling errors that occur when working with the database"""
        if exception_type:
            await self.session.rollback()
            await self.session.close()

            if issubclass(exception_type, DatabaseError) or issubclass(exception_type, DBAPIError):
                raise self._create_strict_db_exception(exception) from exception  # type: ignore
            else:
                raise exception_type(exception) from exception

        try:
            await self.session.commit()
        except DatabaseError as ex:
            await self.session.rollback()
            raise self._create_strict_db_exception(ex) from ex
        except Exception as ex:
            await self.session.rollback()
            raise ex
        finally:
            with suppress(Exception):
                await self.session.close()

    def __enter__(self) -> Session:
        assert not self._is_async, "This is async session!"
        self.session.begin()
        return self.session

    def __exit__(self, exception_type: type, exception: Exception, _traceback) -> None:
        if exception_type:
            self.session.rollback()
            self.session.close()

            if issubclass(exception_type, DatabaseError) or issubclass(exception_type, DBAPIError):
                raise self._create_strict_db_exception(exception) from exception  # type: ignore
            else:
                raise exception_type(exception) from exception

        try:
            self.session.commit()
        except DatabaseError as ex:
            self.session.rollback()
            raise self._create_strict_db_exception(ex) from ex
        except Exception as ex:
            self.session.rollback()
            raise ex
        finally:
            with suppress(Exception):
                self.session.close()

    @staticmethod
    def _create_strict_db_exception(
        common_exception: DatabaseError,
    ) -> DatabaseException:
        strict_exception = DatabaseException
        if hasattr(common_exception.orig, "sqlstate"):
            strict_exception = SQLSTATE_TO_DB_EXCEPTION_HM.get(common_exception.orig.sqlstate) or strict_exception
        reason = re.sub(r"<[^>]*>: ", "", str(common_exception.orig))
        return strict_exception(reason)


class PostgreSQL(BaseService, Database):  # pylint: disable=too-many-instance-attributes
    """
    Implementing a PostgreSQL database
    - loading table metadata from the database (_prepare_metadata)
    - preparation of objects for group insertion (_prepare_objects)
    - perform bulk insert (bulk_create)
    - when receiving metadata, they are stored in the dictionary, for caching (_fetched_tables)
    """

    _username: str
    _password: str
    _host: str
    _port: int
    _database: str
    _echo_pool: Literal["debug"] | bool
    _pool_size: int
    _connection_retry_period_sec: float

    _async_engine: engine.AsyncEngine
    _sync_engine: engine.Engine

    _metadata: MetaData

    _async_session_maker: async_sessionmaker[AsyncSession]
    _sync_session_maker: sessionmaker[Session]

    _fetched_tables: dict[str, Table]

    _async_session: AsyncSession
    _sync_session: Session

    _autocommit: bool

    def __init__(
        self,
        username: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        echo_pool: Literal["debug"] | bool = False,
        pool_size: int = 10,
        connection_retry_period_sec: float = 5,
    ):
        """
        Initialize settings
        :param connection_params(PostgreSQLParams): Database connection parameters and settings for working with it
        """
        super().__init__()
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._database = database
        self._echo_pool = echo_pool
        self._pool_size = pool_size
        self._connection_retry_period_sec = connection_retry_period_sec
        self._fetched_tables = {}
        self._metadata = MetaData()
        self._base = declarative_base(metadata=self._metadata)
        self._autocommit = True

        self.connect()

    @property
    def engine(self) -> engine.AsyncEngine:
        return self._async_engine

    def _async_make_url(self) -> str:
        """An example of a private method for generating a connection string"""
        return (
            f"postgresql+asyncpg://{quote(self._username)}:"
            f"{quote(self._password)}@{self._host}:{self._port}/{self._database}"
        )

    def _sync_make_url(self) -> str:
        """An example of a private method for generating a connection string"""
        return (
            f"postgresql://{quote(self._username)}:"
            f"{quote(self._password)}@{self._host}:{self._port}/{self._database}"
        )

    def connect(self) -> None:
        """Database connecting"""

        try:
            self._async_engine = create_async_engine(
                url=self._async_make_url(),
                pool_size=self._pool_size,
                echo_pool=self._echo_pool,
                pool_pre_ping=True,
                connect_args={
                    "server_settings": {
                        # "statement_timeout": "20000",
                    },
                },
            )
            self._sync_engine = create_engine(
                url=self._sync_make_url(),
                pool_size=self._pool_size,
                echo_pool=self._echo_pool,
                pool_pre_ping=True,
            )

            self._async_session_maker = async_sessionmaker(bind=self._async_engine, expire_on_commit=False)
            self._sync_session_maker = sessionmaker(bind=self._sync_engine, expire_on_commit=False)
        except socket.gaierror:
            raise

    def session(self) -> SessionHandler:
        """Create an intermediate async session"""
        return SessionHandler(async_session=self._async_session_maker())

    def sync_session(self) -> SessionHandler:
        """Create an intermediate sync session"""
        return SessionHandler(sync_session=self._sync_session_maker())

    async def start(self):
        """
        Run actions for starting a service
        """
        pass

    async def stop(self):
        """
        Run actions for stopping a service
        """
        pass

    async def healthcheck(self) -> tuple[bool, str]:
        try:
            is_working, reason = True, ""
            async with self.session() as _session:
                await _session.execute(text("SELECT 1"))
        except Exception as err:
            is_working, reason = False, str(err)

        return is_working, reason
