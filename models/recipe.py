from typing import List
from connection_pool import get_connection
from models.ingredient import Ingredient
import pytz
import datetime
import RecipeDatabase as rdb


class Recipe:
    def __init__(self, name: str, owner_id: int, timestamp: float = None, _id: int = None):
        self.id = _id
        self.name = name
        self.owner_id = owner_id
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"User({self.name!r}, {self.owner_id!r}, {self.timestamp!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            self.timestamp = current_datetime_utc.timestamp()
            new_recipe_id = rdb.create_recipe(connection, self.name, self.owner_id, self.timestamp)
            self.id = new_recipe_id

    def add_ingredient(self, name:str, quantity: float, unit: str, group: str):
        Ingredient(self.id, name, quantity, unit, group).save()

    def log_recipe_on_grocery(self):
        with get_connection() as connection:
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            timestamp = current_datetime_utc.timestamp()
            rdb.log_recipe_4_grocery(connection, self.id, timestamp)

    @classmethod
    def all(cls, user_id: int) -> List["Recipe"]:
        with get_connection() as connection:
            recipes = rdb.get_recipes(connection, user_id)
            return [cls(recipe[1], recipe[2], recipe[3], recipe[0]) for recipe in recipes]

    @classmethod
    def get(cls, recipe_id: int) -> "Recipe":
        with get_connection() as connection:
            recipe = rdb.get_recipe(connection, recipe_id)
            return cls(recipe[1], recipe[2], recipe[3], recipe[0])

