from typing import List, Tuple, Dict
from connection_pool import get_connection
import pytz
import datetime
import RecipeDatabase as rdb


class Grocery:
    def __init__(self, name: str, quantity: float, unit: str, group: str, list_ind: int = 1,
                 _id: int = None):
        self.id = _id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.group = group
        self.list_ind = list_ind

    def __repr__(self) -> str:
        return f"User({self.name!r}, {self.quantity!r}, {self.unit!r}, {self.group!r}, " \
            f"{self.list_ind!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            new_grocery_item_id = rdb.add_grocery_item(connection, self.name, self.quantity, self.unit,
                                                       self.group, self.list_ind)
            self.id = new_grocery_item_id

    @classmethod
    def get(cls) -> List["Grocery"]:
        with get_connection() as connection:
            grocery_list = rdb.get_grocery_items(connection)
            return [cls(grocery_item[1], grocery_item[2], grocery_item[3], grocery_item[4], grocery_item[5],
                        grocery_item[0]) for grocery_item in grocery_list]
