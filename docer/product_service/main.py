from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Product Service")

# Имитация базы данных товаров
PRODUCTS = {
    1: {"id": 1, "name": "Laptop", "price": 1000.0},
    2: {"id": 2, "name": "Smartphone", "price": 500.0},
    3: {"id": 3, "name": "Headphones", "price": 100.0},
}

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = PRODUCTS.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product