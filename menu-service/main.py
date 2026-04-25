from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker


app = FastAPI(title="Italian Restaurant Menu Service")

DATABASE_URL = "postgresql://restaurant_user:restaurant_password@postgres-service:5432/restaurant_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class MenuItemDB(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float)
    
    __table_args__ = (
        UniqueConstraint("name", name="unique_menu_item_name"),
    )


Base.metadata.create_all(bind=engine)


class MenuItem(BaseModel):
    name: str
    category: str
    price: float


def seed_menu():
    db = SessionLocal()
    existing_items = db.query(MenuItemDB).count()

    if existing_items == 0:
        initial_menu = [
            MenuItemDB(name="Bruschetta tomate basilic", category="Entrée", price=6.50),
            MenuItemDB(name="Antipasti italiens", category="Entrée", price=9.00),
            MenuItemDB(name="Salade Caprese", category="Entrée", price=7.50),
            MenuItemDB(name="Arancini siciliens", category="Entrée", price=8.00),

            MenuItemDB(name="Pizza Margherita", category="Pizza", price=9.50),
            MenuItemDB(name="Pizza Regina", category="Pizza", price=11.50),
            MenuItemDB(name="Pizza Quattro Formaggi", category="Pizza", price=12.00),
            MenuItemDB(name="Pizza Diavola", category="Pizza", price=12.50),
            MenuItemDB(name="Pizza Végétarienne", category="Pizza", price=11.00),

            MenuItemDB(name="Spaghetti Carbonara", category="Plat", price=10.50),
            MenuItemDB(name="Lasagne alla Bolognese", category="Plat", price=12.50),
            MenuItemDB(name="Penne Arrabbiata", category="Plat", price=9.80),
            MenuItemDB(name="Risotto aux champignons", category="Plat", price=13.00),
            MenuItemDB(name="Escalope Milanaise", category="Plat", price=14.50),

            MenuItemDB(name="Tiramisu", category="Dessert", price=5.50),
            MenuItemDB(name="Panna Cotta fruits rouges", category="Dessert", price=5.00),
            MenuItemDB(name="Cannoli siciliens", category="Dessert", price=6.00),
            MenuItemDB(name="Gelato vanille chocolat", category="Dessert", price=4.50),

            MenuItemDB(name="Eau minérale", category="Boisson", price=2.50),
            MenuItemDB(name="Soda italien", category="Boisson", price=3.50),
            MenuItemDB(name="Café espresso", category="Boisson", price=2.00),
        ]

        db.add_all(initial_menu)
        db.commit()

    db.close()


seed_menu()


def format_menu_item(item):
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "price": item.price
    }


@app.get("/")
def home():
    return {
        "message": "Italian Restaurant Menu Service is running",
        "restaurant": "Bella Italia",
        "database": "PostgreSQL"
    }


@app.get("/menu")
def get_menu():
    db = SessionLocal()
    items = db.query(MenuItemDB).all()
    db.close()

    menu_by_category = {}

    for item in items:
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []

        menu_by_category[item.category].append(format_menu_item(item))

    return {
        "restaurant": "Bella Italia",
        "menu": menu_by_category
    }


@app.get("/menu/category/{category_name}")
def get_menu_by_category(category_name: str):
    db = SessionLocal()
    items = db.query(MenuItemDB).filter(MenuItemDB.category == category_name).all()
    db.close()

    if not items:
        return {"error": "Category not found"}

    return {
        "restaurant": "Bella Italia",
        "category": category_name,
        "items": [format_menu_item(item) for item in items]
    }


@app.get("/menu/item/{item_id}")
def get_menu_item(item_id: int):
    db = SessionLocal()
    item = db.query(MenuItemDB).filter(MenuItemDB.id == item_id).first()
    db.close()

    if item is None:
        return {"error": "Menu item not found"}

    return format_menu_item(item)


@app.post("/menu")
def create_menu_item(item: MenuItem):
    db = SessionLocal()

    existing_item = db.query(MenuItemDB).filter(MenuItemDB.name == item.name).first()

    if existing_item:
        db.close()
        return {
            "error": "Menu item already exists",
            "message": f"The item '{item.name}' already exists in the menu."
        }

    new_item = MenuItemDB(
        name=item.name,
        category=item.category,
        price=item.price
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()

    return {
        "message": "Menu item created",
        "item": format_menu_item(new_item)
    }

@app.put("/menu/item/{item_id}")
def update_menu_item(item_id: int, updated_item: MenuItem):
    db = SessionLocal()

    item = db.query(MenuItemDB).filter(MenuItemDB.id == item_id).first()

    if item is None:
        db.close()
        return {"error": "Menu item not found"}

    item_with_same_name = (
        db.query(MenuItemDB)
        .filter(MenuItemDB.name == updated_item.name, MenuItemDB.id != item_id)
        .first()
    )

    if item_with_same_name:
        db.close()
        return {
            "error": "Menu item name already exists",
            "message": f"Another item already uses the name '{updated_item.name}'."
        }

    item.name = updated_item.name
    item.category = updated_item.category
    item.price = updated_item.price

    db.commit()
    db.refresh(item)
    db.close()

    return {
        "message": "Menu item updated",
        "item": format_menu_item(item)
    }

@app.delete("/menu/item/{item_id}")
def delete_menu_item(item_id: int):
    db = SessionLocal()
    item = db.query(MenuItemDB).filter(MenuItemDB.id == item_id).first()

    if item is None:
        db.close()
        return {"error": "Menu item not found"}

    deleted_item = format_menu_item(item)

    db.delete(item)
    db.commit()
    db.close()

    return {
        "message": "Menu item deleted",
        "item": deleted_item
    }