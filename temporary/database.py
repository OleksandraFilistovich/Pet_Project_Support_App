from dataclasses import dataclass
from typing import Any


class DataMapper:
    def __init__(self, schema: object) -> None:
        self._schema = schema

    def _connect(self):
        self._session = None

    def create_table_if_not_exist(self):
        table_name = "".join(self.__class__.__name__.lower(), "s")
        query = f"CREATE TABLE IF NOT EXIST {table_name}"
        self.__session.execute(query)

class Schema:
    def __init__(self):
        self._mapper = DataMapper(self)

    id: int

    def save(self):
        self._mapper.insert(self.username)

    def delete(self, id: int):
        ...

    def get(self, key: str, value: Any):
        self._mapper.select()
        ...

@dataclass
class User(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str

@dataclass
class Request(Schema):
    title: str
    text: str
    visibility: int
    user_id: int
    manager_id: int

@dataclass
class Message(Schema):
    user_id: int
    request_id: int


john = User(
    id = 1, 
    username = "john", 
    email = "1@gmail.com", 
    password="2222"
)

john.save()
