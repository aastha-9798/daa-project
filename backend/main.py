from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import itertools

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VehicleDimensions(BaseModel):
    length: float
    breadth: float
    height: float

def get_padding_factor(fragility_index: int) -> float:
    return 1 + 0.02 * fragility_index

def generate_rotations(length: float, breadth: float, height: float):
    return set(itertools.permutations([length, breadth, height]))

def compute_volume(p: Dict) -> float:
    return p["padded_length"] * p["padded_breadth"] * p["padded_height"]

def preprocess_products(products: List[Dict]) -> List[Dict]:
    for product in products:
        factor = get_padding_factor(product["fragility_index"])
        product["padded_length"] = product["length"] * factor
        product["padded_breadth"] = product["breadth"] * factor
        product["padded_height"] = product["height"] * factor
    return products

def pack_products(vehicle: Dict[str, float], products: List[Dict]) -> List[Dict]:
    v_length, v_breadth, v_height = vehicle["length"], vehicle["breadth"], vehicle["height"]

    products = preprocess_products(products)
    products.sort(key=compute_volume, reverse=True)

    packed_items = []
    x, y, z = 0, 0, 0
    max_layer_height = 0
    max_row_breadth = 0

    for product in products:
        fit = False
        rotations = generate_rotations(product["padded_length"], product["padded_breadth"], product["padded_height"])

        for rot in rotations:
            p_len, p_br, p_ht = rot
            if (x + p_len <= v_length) and (y + p_br <= v_breadth) and (z + p_ht <= v_height):
                fit = True
                break

        if not fit:
            continue

        packed_items.append({
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "fragility_index": product["fragility_index"],
            "adjusted_size": {
                "length": round(p_len, 2),
                "breadth": round(p_br, 2),
                "height": round(p_ht, 2)
            },
            "position": {
                "x": round(x, 2),
                "y": round(y, 2),
                "z": round(z, 2)
            }
        })

        x += p_len
        max_row_breadth = max(max_row_breadth, p_br)
        max_layer_height = max(max_layer_height, p_ht)

        if x >= v_length:
            x = 0
            y += max_row_breadth
            max_row_breadth = 0

        if y >= v_breadth:
            y = 0
            z += max_layer_height
            max_layer_height = 0

        if z >= v_height:
            break

    return packed_items

# ✅ New endpoint for receiving vehicle dimensions
@app.post("/vehicle")
def receive_vehicle(vehicle: VehicleDimensions):
    print(f"Received vehicle dimensions: {vehicle}")
    return {"message": "Vehicle dimensions received successfully"}

@app.post("/pack")
def pack_vehicle_space(vehicle: VehicleDimensions):
    try:
        with open("products.json", "r") as f:
            products = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load product data")

    packed = pack_products(vehicle.dict(), products)
    return {"packed_items": packed}
