from connection_pool import get_connection
import pytz
import datetime
import RecipeDatabase as rdb


class AppUser:
    def __init__(self, username: str, password: str, timestamp: float = None, _id: int = None):
        self.id = _id
        self.username = username
        self.password = password
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"User({self.username!r}, {self.password!r}, {self.timestamp!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            self.timestamp = current_datetime_utc.timestamp()
            new_user_id = rdb.add_user(connection, self.username, self.password, self.timestamp)
            self.id = new_user_id

    def verify(self, password: str):
        if password == self.password:
            return True

    @classmethod
    def get(cls, username: str) -> "AppUser":
        with get_connection() as connection:
            appuser = rdb.get_user(connection, username)
            return cls(appuser[1], appuser[2], appuser[3], appuser[0])
