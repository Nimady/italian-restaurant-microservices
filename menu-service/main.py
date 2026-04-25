from fastapi import FastAPI

app = FastAPI(title="Italian Restaurant Menu Service")

menu = {
    "restaurant": "Bella Italia",
    "menu": {
        "entrees": [
            {"id": 1, "name": "Bruschetta tomate basilic", "price": 6.50},
            {"id": 2, "name": "Antipasti italiens", "price": 9.00},
            {"id": 3, "name": "Salade Caprese", "price": 7.50},
            {"id": 4, "name": "Arancini siciliens", "price": 8.00}
        ],
        "pizzas": [
            {"id": 5, "name": "Pizza Margherita", "price": 9.50},
            {"id": 6, "name": "Pizza Regina", "price": 11.50},
            {"id": 7, "name": "Pizza Quattro Formaggi", "price": 12.00},
            {"id": 8, "name": "Pizza Diavola", "price": 12.50},
            {"id": 9, "name": "Pizza Végétarienne", "price": 11.00}
        ],
        "plats": [
            {"id": 10, "name": "Spaghetti Carbonara", "price": 10.50},
            {"id": 11, "name": "Lasagne alla Bolognese", "price": 12.50},
            {"id": 12, "name": "Penne Arrabbiata", "price": 9.80},
            {"id": 13, "name": "Risotto aux champignons", "price": 13.00},
            {"id": 14, "name": "Escalope Milanaise", "price": 14.50}
        ],
        "desserts": [
            {"id": 15, "name": "Tiramisu", "price": 5.50},
            {"id": 16, "name": "Panna Cotta fruits rouges", "price": 5.00},
            {"id": 17, "name": "Cannoli siciliens", "price": 6.00},
            {"id": 18, "name": "Gelato vanille chocolat", "price": 4.50}
        ],
        "boissons": [
            {"id": 19, "name": "Eau ", "price": 2.50},
            {"id": 20, "name": "Soda ", "price": 3.50},
            {"id": 21, "name": "Café espresso", "price": 2.00}
        ]
    }
}


@app.get("/")
def home():
    return {
        "message": "Italian Restaurant Menu Service is running",
        "restaurant": "Bella Italia"
    }


@app.get("/menu")
def get_menu():
    return menu


@app.get("/menu/category/{category_name}")
def get_menu_by_category(category_name: str):
    categories = menu["menu"]

    if category_name in categories:
        return {
            "restaurant": menu["restaurant"],
            "category": category_name,
            "items": categories[category_name]
        }

    return {"error": "Category not found"}


@app.get("/menu/item/{item_id}")
def get_menu_item(item_id: int):
    for category_name, items in menu["menu"].items():
        for item in items:
            if item["id"] == item_id:
                return {
                    "restaurant": menu["restaurant"],
                    "category": category_name,
                    "item": item
                }

    return {"error": "Menu item not found"}