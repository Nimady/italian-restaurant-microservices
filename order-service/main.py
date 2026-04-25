from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests

app = FastAPI(title="Italian Restaurant Order Service")

class Order(BaseModel):
    customer_name: str
    items: List[str]
    total: float

orders = [
    {
        "id": 1,
        "customer_name": "Nimad",
        "items": ["Pizza Margherita", "Tiramisu"],
        "total": 15.00,
        "status": "preparing"
    },
    {
        "id": 2,
        "customer_name": "Sara",
        "items": ["Lasagne alla Bolognese", "Panna Cotta"],
        "total": 17.50,
        "status": "ready"
    }
]


@app.get("/")
def home():
    return {
        "message": "Italian Restaurant Order Service is running",
        "restaurant": "Bella Italia"
    }


@app.get("/orders")
def get_orders():
    return orders


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["id"] == order_id:
            return order
    return {"error": "Order not found"}


@app.post("/orders")
def create_order(order: Order):
    new_order = {
        "id": len(orders) + 1,
        "customer_name": order.customer_name,
        "items": order.items,
        "total": order.total,
        "status": "received"
    }

    orders.append(new_order)
    return new_order

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