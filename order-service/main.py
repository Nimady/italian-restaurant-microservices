from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker


app = FastAPI(title="Italian Restaurant Order Service")

DATABASE_URL = "sqlite:///./orders.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

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
    total: float


class OrderStatus(BaseModel):
    status: str


def format_order(order):
    return {
        "id": order.id,
        "customer_number": order.customer_number,
        "items": order.items.split(","),
        "total": order.total,
        "status": order.status
    }


@app.get("/")
def home():
    return {
        "message": "Italian Restaurant Order Service is running",
        "restaurant": "Bella Italia",
        "database": "SQLite"
    }


@app.get("/orders")
def get_orders():
    db = SessionLocal()
    orders = db.query(OrderDB).all()
    db.close()

    return [format_order(order) for order in orders]


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    db = SessionLocal()
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    db.close()

    if order is None:
        return {"error": "Order not found"}

    return format_order(order)


@app.post("/orders")
def create_order(order: Order):
    db = SessionLocal()

    new_order = OrderDB(
        customer_number=order.customer_number,
        items=",".join(order.items),
        total=order.total,
        status="received"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    db.close()

    return {
        "message": "Order created",
        "order": format_order(new_order)
    }


@app.put("/orders/{order_id}")
def update_order(order_id: int, updated_order: Order):
    db = SessionLocal()

    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

    if order is None:
        db.close()
        return {"error": "Order not found"}

    order.customer_number = updated_order.customer_number
    order.items = ",".join(updated_order.items)
    order.total = updated_order.total

    db.commit()
    db.refresh(order)
    db.close()

    return {
        "message": "Order updated",
        "order": format_order(order)
    }


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, order_status: OrderStatus):
    db = SessionLocal()

    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

    if order is None:
        db.close()
        return {"error": "Order not found"}

    order.status = order_status.status

    db.commit()
    db.refresh(order)
    db.close()

    return {
        "message": "Order status updated",
        "order": format_order(order)
    }


@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    db = SessionLocal()

    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()

    if order is None:
        db.close()
        return {"error": "Order not found"}

    deleted_order = format_order(order)

    db.delete(order)
    db.commit()
    db.close()

    return {
        "message": "Order deleted",
        "order": deleted_order
    }


@app.get("/menu-from-service")
def get_menu_from_menu_service():
    try:
        response = requests.get("http://menu-service:8000/menu")
        return {
            "message": "Menu received from menu-service",
            "menu": response.json()
        }
    except Exception as e:
        return {
            "error": "Could not connect to menu-service",
            "details": str(e)
        }