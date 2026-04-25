from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import requests

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker


app = FastAPI(title="Italian Restaurant Order Service")

DATABASE_URL = "postgresql://restaurant_user:restaurant_password@postgres-service:5432/restaurant_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_number = Column(Integer, index=True)
    items = Column(String)
    total = Column(Float)
    status = Column(String)


Base.metadata.create_all(bind=engine)


class Order(BaseModel):
    customer_number: int
    items: List[str]


class OrderStatus(BaseModel):
    status: str


def clean_items(items: List[str]) -> List[str]:
    return [item.strip() for item in items if item.strip()]


def format_order(order: OrderDB):
    return {
        "id": order.id,
        "customer_number": order.customer_number,
        "items": order.items.split(",") if order.items else [],
        "total": order.total,
        "status": order.status
    }


def get_menu_prices():
    response = requests.get("http://menu-service:8000/menu", timeout=5)
    response.raise_for_status()

    menu_data = response.json()["menu"]
    prices = {}

    for category_items in menu_data.values():
        for item in category_items:
            prices[item["name"].lower()] = item["price"]

    return prices


def calculate_total(items: List[str]) -> Optional[float]:
    prices = get_menu_prices()
    total = 0

    for item_name in items:
        key = item_name.lower()

        if key not in prices:
            return None

        total += prices[key]

    return round(total, 2)


@app.get("/")
def home():
    return {
        "message": "Italian Restaurant Order Service is running",
        "restaurant": "Bella Italia",
        "database": "PostgreSQL"
    }


@app.get("/orders")
def get_orders():
    db = SessionLocal()
    try:
        orders = db.query(OrderDB).all()
        return [format_order(order) for order in orders]
    finally:
        db.close()


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

        if order is None:
            return {"error": "Order not found"}

        return format_order(order)
    finally:
        db.close()


@app.post("/orders")
def create_order(order: Order):
    db = SessionLocal()
    try:
        cleaned_items = clean_items(order.items)

        if not cleaned_items:
            return {
                "error": "Empty order",
                "message": "The order must contain at least one item."
            }

        try:
            total = calculate_total(cleaned_items)
        except Exception as e:
            return {
                "error": "Menu service unavailable",
                "message": "Could not calculate total because menu-service is unavailable.",
                "details": str(e)
            }

        if total is None:
            return {
                "error": "Invalid item",
                "message": "One or more items do not exist in the menu."
            }

        new_order = OrderDB(
            customer_number=order.customer_number,
            items=",".join(cleaned_items),
            total=total,
            status="received"
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return {
            "message": "Order created",
            "order": format_order(new_order)
        }
    finally:
        db.close()


@app.put("/orders/{order_id}")
def update_order(order_id: int, updated_order: Order):
    db = SessionLocal()
    try:
        order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

        if order is None:
            return {"error": "Order not found"}

        cleaned_items = clean_items(updated_order.items)

        if not cleaned_items:
            return {
                "error": "Empty order",
                "message": "The order must contain at least one item."
            }

        try:
            total = calculate_total(cleaned_items)
        except Exception as e:
            return {
                "error": "Menu service unavailable",
                "message": "Could not calculate total because menu-service is unavailable.",
                "details": str(e)
            }

        if total is None:
            return {
                "error": "Invalid item",
                "message": "One or more items do not exist in the menu."
            }

        order.customer_number = updated_order.customer_number
        order.items = ",".join(cleaned_items)
        order.total = total

        db.commit()
        db.refresh(order)

        return {
            "message": "Order updated",
            "order": format_order(order)
        }
    finally:
        db.close()


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, order_status: OrderStatus):
    db = SessionLocal()
    try:
        order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

        if order is None:
            return {"error": "Order not found"}

        order.status = order_status.status

        db.commit()
        db.refresh(order)

        return {
            "message": "Order status updated",
            "order": format_order(order)
        }
    finally:
        db.close()


@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

        if order is None:
            return {"error": "Order not found"}

        deleted_order = format_order(order)

        db.delete(order)
        db.commit()

        return {
            "message": "Order deleted",
            "order": deleted_order
        }
    finally:
        db.close()


@app.get("/menu-from-service")
def get_menu_from_menu_service():
    try:
        response = requests.get("http://menu-service:8000/menu", timeout=5)
        response.raise_for_status()

        return {
            "message": "Menu received from menu-service",
            "menu": response.json()
        }
    except Exception as e:
        return {
            "error": "Could not connect to menu-service",
            "details": str(e)
        }