from connection_pool import get_connection
import RecipeDatabase as rdb
from models.rec_app_user import AppUser
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.grocery import Grocery
import datetime
import pytz
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER

USER_PROMPT = "Do you have an existing account? (y/N): "

USERNAME_PROMPT = "Please enter a username: "

PASSWORD_PROMPT = "Please enter a password: "

NEW_INGREDIENT_PROMPT = "Please enter an ingredient (Press ENTER to end): "

QUANTITY_PROMPT = "Please enter a quantity (decimal form): "

UNIT_PROMPT = """Chose unit from the list:
cup
fl.oz.
tbs
tsp
pinch
dash
gram
lb
oz
pack
bag
jar
can
whole
to taste

Please enter the unit: """

GROUP_PROMPT = """Chose grocery group from the list:
P = Produce
M = Meat
D = Dairy
C = Canned Goods
S = Spices
SO = Sauces and/or Oils
F = Frozen
R = Other

Please enter the letter for grocery group: """

MAIN_MENU_PROMPT = """ -- MENU --

1) Create New Recipe
2) View All Recipes
3) View Selected Recipe
4) Edit Existing Recipe
5) Delete Existing Recipe
6) Create Grocery List
7) Exit

Please enter your choice: """

RECIPE_EDIT_CHOICE_PROMPT = "Please select recipe edit option (Add, Delete, or Edit) ingredient (press ENTER to END): "

EDIT_INGREDIENT_PROMPT = "Please enter ID for ingredient you would like to edit: "

DELETE_INGREDIENT_PROMPT = "Please enter ID for ingredient you would like to delete: "

DELETE_RECIPE_PROMPT = "Please enter ID for recipe you would like to delete (press ENTER to end): "

GROCERY_LIST_RECIPE_PROMPT = "Please enter the ID for 1 recipe you would like groceries for (press Enter to end): "

UNIT_LIST = ["cup", "fl.oz.", "tbs", "tsp", "pinch", "gram", "lb", "oz", "pack", "bag", "jar", "can", "whole",
             "to taste", "dash"]
GROUP_LIST = ["Produce", "Meat", "Dairy", "Canned Goods", "Spices", "Sauces and/or Oils", "Frozen", "Other"]
GROUP_LIST_SYMBOL = ["P", "M", "D", "C", "S", "SO", "F", "R"]
GROUP_LIST_SYMBOL_GROCERY = ["P ", "M ", "D ", "C ", "S ", "SO", "F ", "R "]


def new_user_create():
    username = input(USERNAME_PROMPT)
    username = username.lower()
    password = input(PASSWORD_PROMPT)
    user = AppUser(username, password)
    user.save()
    return user.username, user.id


def user_login():
    username = input(USERNAME_PROMPT)
    username = username.lower()
    password = input(PASSWORD_PROMPT)
    user = AppUser.get(username)
    pass_check = user.verify(password)

    if pass_check:
        return user.username, user.id
    else:
        return "fail", "nope"


def prompt_create_recipe(user_id):
    recipe_name = input("Enter recipe name: ")
    recipe = Recipe(recipe_name, user_id)
    recipe.save()

    add_ingredients_to_recipe(recipe)


def add_ingredients_to_recipe(recipe):
    new_ingredient = input(NEW_INGREDIENT_PROMPT)
    while new_ingredient:
        quantity = input(QUANTITY_PROMPT)
        quantity = float(quantity)
        wrong_unit = True
        while wrong_unit:
            unit = input(UNIT_PROMPT)
            unit = unit.lower()
            if unit not in UNIT_LIST:
                print("Please re-enter unit.")
            else:
                wrong_unit = False
        wrong_group = True
        while wrong_group:
            group = input(GROUP_PROMPT)
            group = group.upper()
            if group not in GROUP_LIST_SYMBOL:
                print("Please re-enter group.")
            else:
                wrong_group = False
        recipe.add_ingredient(new_ingredient, quantity, unit, group)
        new_ingredient = input(NEW_INGREDIENT_PROMPT)


def view_all_recipes(user_id):
    for recipe in Recipe.all(user_id):
        naive_datetime = datetime.datetime.utcfromtimestamp(recipe.timestamp)
        utc_date = pytz.utc.localize(naive_datetime)
        local_date = utc_date.astimezone(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M")
        print(f"{recipe.id}: {recipe.name}  -- Created on: {local_date}")


def prompt_view_single_recipe(user_id):
    view_all_recipes(user_id)
    recipe_id = int(input("Please enter the recipe id for the recipe you would like to view: "))
    multiplier = input("Please enter a multiplier in decimal form: ")
    multiplier = float(multiplier)
    recipe = Recipe.get(recipe_id)
    naive_datetime = datetime.datetime.utcfromtimestamp(recipe.timestamp)
    utc_date = pytz.utc.localize(naive_datetime)
    local_date = utc_date.astimezone(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M")
    print("-----------------")
    print(f"Ingredients List for: {recipe.name}  -- Created on: {local_date}")
    for ingredient in Ingredient.get(recipe_id):
        quantity = float(ingredient.quantity)
        quant = multiplier * quantity
        quant = round(quant, 2)
        print(f"{ingredient.id:2}: {ingredient.name:25}  -  {quant} {ingredient.unit:8}  -- Group = {ingredient.group}")
    return recipe


def prompt_edit_existing_recipe(user_id):
    recipe = prompt_view_single_recipe(user_id)
    choice = input(RECIPE_EDIT_CHOICE_PROMPT).lower()
    while choice:
        if choice == "add":
            add_ingredients_to_recipe(recipe)
        elif choice == "delete":
            ingredient_id = input(DELETE_INGREDIENT_PROMPT)
            ingredient_id = int(ingredient_id)
            ingredient_gone = Ingredient.get_single(ingredient_id)
            ingredient_gone.delete_ingredient()
        else:
            ingredient_id = input(EDIT_INGREDIENT_PROMPT)
            ingredient_id = int(ingredient_id)
            ingredient_gone = Ingredient.get_single(ingredient_id)
            recipe_id = ingredient_gone.recipe_id
            ingredient_gone.delete_ingredient()
            recipe = Recipe.get(recipe_id)
            add_ingredients_to_recipe(recipe)
        choice = input(RECIPE_EDIT_CHOICE_PROMPT).lower()


def prompt_delete_existing_recipe(user_id):
    view_all_recipes(user_id)
    recipe_id = input(DELETE_RECIPE_PROMPT)
    while recipe_id:
        recipe_id = int(recipe_id)
        with get_connection() as connection:
            rdb.delete_recipe(connection, recipe_id)
        view_all_recipes(user_id)
        recipe_id = input(DELETE_RECIPE_PROMPT)


def prompt_create_grocery_list(user_id):
    view_all_recipes(user_id)
    recipe_list = []
    multipliers = []
    scaling = {}
    recipe_4_list = input(GROCERY_LIST_RECIPE_PROMPT)
    while recipe_4_list:
        recipe_4_list = int(recipe_4_list)
        recipe_list.append(recipe_4_list)
        multi = input("Please enter a multiplier in decimal form: ")
        multi = float(multi)
        multipliers.append(multi)
        recipe_4_list = input(GROCERY_LIST_RECIPE_PROMPT)
    # multiplier = multipliers[0]
    for recipe_id_4dict, scalar in zip(recipe_list, multipliers):
        scaling[recipe_id_4dict] = scalar
    recipe_names = []
    for recipe_id in recipe_list:
        recipe_4_log = Recipe.get(recipe_id)
        recipe_names.append(recipe_4_log.name)
        recipe_4_log.log_recipe_on_grocery()
    current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
    timestamp = current_datetime_utc.timestamp()
    naive_datetime = datetime.datetime.utcfromtimestamp(timestamp)
    utc_date = pytz.utc.localize(naive_datetime)
    local_date = utc_date.astimezone(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M")
    pdf_or_not = input("Do you want a PDF printout of Grocery List? (y/N): ")
    print("-----------------------------")
    print(f"Grocery List Generated on: {local_date}")
    print("List includes items from the following recipes:")
    for recipe, multiple in zip(recipe_names, multipliers):
        print(f"{recipe} x {multiple}")
    print("-----------------------------")
    recipe_through = tuple(recipe_list)
    ingredients_4_list = Ingredient.get_for_list(recipe_through)
    for ingredient in ingredients_4_list:
        ingredient.scale_quantity(scaling)
        ingredient.add_ingredient_2_grocery_list()
    groceries = Grocery.get()
    groups_included = []
    for grocery in groceries:
        groups_included.append(grocery.group)
    for category, label in zip(GROUP_LIST_SYMBOL_GROCERY, GROUP_LIST):
        if category in groups_included:
            print(" ")
            print(f"------- {label} -------")
        for grocery in groceries:
            if grocery.group == category:
                print(f"{grocery.name:25}  -  {grocery.quantity} {grocery.unit}")
    if pdf_or_not == "y":
        grocery_to_pdf(local_date, recipe_names, groups_included, groceries, multipliers)


def grocery_to_pdf(local_date, recipe_names, groups_included, groceries, multipliers):
    pdf_url = '/Users/timothymannon/PycharmProjects/RecipeApp/GroceryLists/'
    pdf_list_name = pdf_url + "Grocery_list_" + local_date + ".pdf"
    list_pdf = Canvas(pdf_list_name, pagesize=LETTER)
    page_start = 720
    page_inc = 12
    list_pdf.drawString(72, page_start, "-----------------------------")
    page_locator = page_start - page_inc
    list_pdf.drawString(72, page_locator, f"Grocery List Generated on: {local_date}")
    page_locator -= page_inc
    list_pdf.drawString(72, page_locator, "List includes items from the following recipes:")
    page_locator -= page_inc
    for recipe, multiple in zip(recipe_names, multipliers):
        list_pdf.drawString(72, page_locator, f"{recipe} x {multiple}")
        page_locator -= page_inc
    list_pdf.drawString(72, page_locator, "-----------------------------")
    page_locator -= page_inc
    for category, label in zip(GROUP_LIST_SYMBOL_GROCERY, GROUP_LIST):
        if category in groups_included:
            list_pdf.drawString(72, page_locator, " ")
            page_locator -= page_inc
            list_pdf.drawString(72, page_locator, f"------- {label} -------")
            page_locator -= page_inc
        for grocery in groceries:
            if grocery.group == category:
                list_pdf.drawString(72, page_locator, f"{grocery.name:25}  -  {grocery.quantity} {grocery.unit}")
                page_locator -= page_inc
    list_pdf.save()


MENU_OPTIONS = {
    "1": prompt_create_recipe,
    "2": view_all_recipes,
    "3": prompt_view_single_recipe,
    "4": prompt_edit_existing_recipe,
    "5": prompt_delete_existing_recipe,
    "6": prompt_create_grocery_list
}


def start_menu():
    with get_connection() as connection:
        rdb.create_tables(connection)

    user_status = input(USER_PROMPT)
    if user_status == "y":
        username, user_id = user_login()
    else:
        username, user_id = new_user_create()

    if username != "fail":
        print(f" -- Welcome {username} to the recipe app! --")
        selection = input(MAIN_MENU_PROMPT)
        while selection != "7":
            try:
                MENU_OPTIONS[selection](user_id)
            except KeyError:
                print("Not a valid inout, please try again!")
            selection = input(MAIN_MENU_PROMPT)
    else:
        print("Incorrect password, please try again")


start_menu()
