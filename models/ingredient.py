from typing import List, Tuple, Dict
from connection_pool import get_connection
from models.grocery import Grocery
import pytz
import datetime
import RecipeDatabase as rdb


class Ingredient:
    def __init__(self, recipe_id: int, name: str, quantity: float, unit: str, group: str, timestamp: float = None,
                 _id: int = None):
        self.id = _id
        self.recipe_id = recipe_id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.group = group
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"User({self.recipe_id!r}, {self.name!r}, {self.quantity!r}, {self.unit!r}, {self.group!r}, " \
            f"{self.timestamp!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            self.timestamp = current_datetime_utc.timestamp()
            new_ingredient_id = rdb.add_ingredient(connection, self.recipe_id, self.name, self.quantity, self.unit,
                                                   self.group, self.timestamp)
            self.id = new_ingredient_id

    def delete_ingredient(self):
        with get_connection() as connection:
            rdb.delete_ingredient(connection, self.id)

    def scale_quantity(self, scaling: Dict):
        quantity = float(self.quantity)
        multiplier = scaling[self.recipe_id]
        quant = multiplier * quantity
        quant = round(quant, 2)
        self.quantity = quant

    def add_ingredient_2_grocery_list(self):
        Grocery(self.name, self.quantity, self.unit, self.group).save()

    @classmethod
    def get(cls, recipe_id: int) -> List["Ingredient"]:
        with get_connection() as connection:
            ingredients = rdb.get_recipe_ingredients(connection, recipe_id)
            return [cls(ingredient[1], ingredient[2], ingredient[3], ingredient[4], ingredient[5], ingredient[6],
                        ingredient[0]) for ingredient in ingredients]

    @classmethod
    def get_single(cls, ingredient_id: int) -> "Ingredient":
        with get_connection() as connection:
            ingredient = rdb.get_single_ingredient(connection, ingredient_id)
            return cls(ingredient[1], ingredient[2], ingredient[3], ingredient[4], ingredient[5], ingredient[6],
                       ingredient[0])

    @classmethod
    def get_for_list(cls, recipe_id: Tuple) -> List["Ingredient"]:
        with get_connection() as connection:
            ingredients = rdb.get_ingredients_for_grocery(connection, recipe_id)
            return [cls(ingredient[1], ingredient[2], ingredient[3], ingredient[4], ingredient[5], ingredient[6],
                        ingredient[0]) for ingredient in ingredients]
