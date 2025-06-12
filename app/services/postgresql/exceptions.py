class DatabaseException(Exception):
    pass


class ObjectAlreadyExistsException(DatabaseException):
    pass


class TableNotFoundException(DatabaseException):
    pass


class ForeignKeyNotFoundException(DatabaseException):
    pass


class IncorrectColumnValueException(DatabaseException):
    pass
