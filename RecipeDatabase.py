from typing import List, Tuple

Recipe = Tuple[int, str, int, float]
Ingredient = Tuple[int, int, str, float, str, str, float]
Grocery = Tuple[int, str, float, str, str, int]

CREATE_USERS = """CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT, password TEXT, 
user_timestamp INTEGER);"""
CREATE_RECIPES = """CREATE TABLE IF NOT EXISTS recipes (id SERIAL PRIMARY KEY, name TEXT, user_id INTEGER, 
recipe_timestamp INTEGER, FOREIGN KEY(user_id) REFERENCES users (id));"""
CREATE_INGREDIENTS = """CREATE TABLE IF NOT EXISTS ingredients 
(id SERIAL PRIMARY KEY, recipe_id INTEGER, ingredient_name TEXT, quantity DECIMAL, unit_name TEXT, group_name CHAR(2), 
ingr_timestamp INTEGER, FOREIGN KEY (recipe_id) REFERENCES recipes (id));"""
CREATE_LIST_LOG = """CREATE TABLE IF NOT EXISTS listlog (id SERIAL PRIMARY KEY, recipe_id INTEGER, 
list_timestamp INTEGER, FOREIGN KEY (recipe_id) REFERENCES recipes (id));"""
CREATE_GROCERY_LIST = """CREATE TABLE IF NOT EXISTS grocery 
(id SERIAL PRIMARY KEY, ingredient_name TEXT, quantity DECIMAL, unit_name TEXT, group_name CHAR(2), 
list_ind INTEGER);"""

INSERT_USER_RETURN_ID = "INSERT INTO users (username, password, user_timestamp) VALUES (%s, %s, %s) RETURNING id;"
INSERT_RECIPE_RETURN_ID = "INSERT INTO recipes (name, user_id, recipe_timestamp) VALUES (%s, %s, %s) RETURNING id;"
INSERT_INGREDIENT_RETURN_ID = """INSERT INTO ingredients (recipe_id, ingredient_name, quantity, unit_name, group_name, 
ingr_timestamp) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"""
INSERT_GROCERY_ITEM_RETURN_ID = """INSERT INTO grocery (ingredient_name, quantity, unit_name, group_name, list_ind) 
VALUES (%s, %s, %s, %s, %s) RETURNING id;"""
INSERT_GROCERY_LOG_ITEM = "INSERT INTO listlog (recipe_id, list_timestamp) VALUES (%s, %s);"

SELECT_USER = "SELECT * FROM users WHERE username = %s;"
SELECT_ALL_RECIPES = "SELECT * FROM recipes WHERE user_id = %s;"
SELECT_SINGLE_RECIPE = "SELECT * FROM recipes WHERE id = %s;"
SELECT_RECIPE_INGREDIENTS = "SELECT * FROM ingredients WHERE recipe_id = %s;"
SELECT_SINGLE_INGREDIENT = "SELECT * FROM ingredients WHERE id = %s;"
SELECT_INGREDIENTS_FOR_GROCERY = "SELECT * FROM ingredients WHERE recipe_id IN %s;"
SELECT_GROCERY_ITEMS = """SELECT SUM(id), ingredient_name, SUM(quantity), unit_name, group_name, SUM(list_ind)
FROM grocery GROUP BY ingredient_name, unit_name, group_name;"""

DELETE_INGREDIENT = "DELETE FROM ingredients WHERE id = %s;"
DELETE_RECIPE_INGREDIENTS = "DELETE FROM ingredients WHERE recipe_id = %s;"
DELETE_RECIPE = "DELETE FROM recipes WHERE id = %s;"
DELETE_GROCERY_LIST = "DELETE FROM grocery WHERE list_ind = %s;"


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS)
            cursor.execute(CREATE_RECIPES)
            cursor.execute(CREATE_INGREDIENTS)
            cursor.execute(CREATE_LIST_LOG)
            cursor.execute(CREATE_GROCERY_LIST)


def add_user(connection, username: str, password: str, timestamp: float) -> int:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_USER_RETURN_ID, (username, password, timestamp))

            user_id = cursor.fetchone()[0]
            return user_id


def get_user(connection, username: str):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER, (username,))
            return cursor.fetchone()


def create_recipe(connection, name: str, owner_id: str, timestamp: float) -> int:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_RECIPE_RETURN_ID, (name, owner_id, timestamp))

            recipe_id = cursor.fetchone()[0]
            return recipe_id


def add_ingredient(connection, recipe_id: int, name: str, quantity: float, unit: str, group: str,
                   timestamp: float) -> int:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_INGREDIENT_RETURN_ID, (recipe_id, name, quantity, unit, group, timestamp))

            ingredient_id = cursor.fetchone()[0]
            return ingredient_id


def get_recipes(connection, user_id: int) -> List[Recipe]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_RECIPES, (user_id,))
            return cursor.fetchall()


def get_recipe(connection, recipe_id: int) -> Recipe:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_SINGLE_RECIPE, (recipe_id,))
            return cursor.fetchone()


def get_recipe_ingredients(connection, recipe_id: int) -> List[Ingredient]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RECIPE_INGREDIENTS, (recipe_id,))
            return cursor.fetchall()


def get_single_ingredient(connection, ingredient_id: int) -> Ingredient:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_SINGLE_INGREDIENT, (ingredient_id,))
            return cursor.fetchone()


def delete_ingredient(connection, ingredient_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_INGREDIENT, (ingredient_id,))


def delete_recipe(connection, recipe_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_RECIPE_INGREDIENTS, (recipe_id,))
            cursor.execute(DELETE_RECIPE, (recipe_id,))


def get_ingredients_for_grocery(connection, recipe_id: Tuple) -> List[Ingredient]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_INGREDIENTS_FOR_GROCERY, (recipe_id,))
            return cursor.fetchall()


def add_grocery_item(connection, name: str, quantity: float, unit: str, group: str, list_ind: int) -> int:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_GROCERY_ITEM_RETURN_ID, (name, quantity, unit, group, list_ind))
            grocery_item_id = cursor.fetchone()[0]
            return grocery_item_id


def get_grocery_items(connection) -> List[Grocery]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_GROCERY_ITEMS)
            grocery_list = cursor.fetchall()
            cursor.execute(DELETE_GROCERY_LIST, (1,))
            return grocery_list


def log_recipe_4_grocery(connection, recipe: int, timestamp: float):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_GROCERY_LOG_ITEM, (recipe, timestamp))
