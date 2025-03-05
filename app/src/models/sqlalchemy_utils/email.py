import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.ext.hybrid import Comparator


class CaseInsensitiveComparator(Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


class EmailType(sa.types.TypeDecorator):
    """
    Provides a way for storing emails in a lower case.
    """

    impl = sa.Unicode
    comparator_factory = CaseInsensitiveComparator
    cache_ok = True

    def __init__(self, length=255, *args, **kwargs):
        super().__init__(length=length, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.lower()
        return value

    @property
    def python_type(self):
        return str
