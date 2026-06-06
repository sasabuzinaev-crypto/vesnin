import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Order Service")

# Получаем URL из окружения с дефолтом на локалхост (для локального запуска)
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:8001")
DISCOUNT_SERVICE_URL = os.getenv("DISCOUNT_SERVICE_URL", "http://127.0.0.1:8003")

class OrderRequest(BaseModel):
    product_id: int
    quantity: int
    promo_code: Optional[str] = None

class OrderResponse(BaseModel):
    product_id: int
    quantity: int
    price_per_unit: float
    total_before_discount: float
    discount_percent: float
    discount_amount: float
    final_total: float

@app.post("/orders", response_model=OrderResponse)
async def create_order(order_req: OrderRequest):
    async with httpx.AsyncClient() as client:
        # 1. Запрос к Product Service
        try:
            prod_res = await client.get(f"{PRODUCT_SERVICE_URL}/products/{order_req.product_id}")
            if prod_res.status_code == 404:
                raise HTTPException(status_code=404, detail="Product not found in product-service")
            product_data = prod_res.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Product service is unavailable")

        price_per_unit = product_data["price"]
        total_before_discount = price_per_unit * order_req.quantity

        # 2. Запрос к Discount Service
        try:
            discount_payload = {
                "product_id": order_req.product_id,
                "quantity": order_req.quantity,
                "price_per_unit": price_per_unit,
                "promo_code": order_req.promo_code
            }
            disc_res = await client.post(f"{DISCOUNT_SERVICE_URL}/discounts/calculate", json=discount_payload)
            discount_data = disc_res.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Discount service is unavailable")

        # 3. Расчет итогов
        discount_percent = discount_data["discount_percent"]
        discount_amount = total_before_discount * (discount_percent / 100)
        final_total = total_before_discount - discount_amount

        return OrderResponse(
            product_id=order_req.product_id,
            quantity=order_req.quantity,
            price_per_unit=price_per_unit,
            total_before_discount=total_before_discount,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            final_total=final_total
        )