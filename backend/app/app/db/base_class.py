import uuid
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        import re
        name_list = re.findall(r"[A-Z][a-z\d]*", cls.__name__)
        return "_".join(name_list).lower()

    @declared_attr
    def __table_args__(cls) -> dict:
        return {'extend_existing': True}

    def dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    def list(self):
        return [getattr(self, c.name, None) for c in self.__table__.columns]


def gen_uuid() -> str:
    return uuid.uuid4().hex