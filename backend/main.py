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

def pack_grouped_products(products_group: List[Dict], spaces: List[tuple], packed_items: List[Dict]):
    for product in products_group:
        placed = False
        rotations = generate_rotations(product["padded_length"], product["padded_breadth"], product["padded_height"])

        for i in range(len(spaces)):
            sx, sy, sz, sl, sb, sh = spaces[i]
            for rot in rotations:
                p_len, p_br, p_ht = rot
                if p_len <= sl and p_br <= sb and p_ht <= sh:
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
                            "x": round(sx, 2),
                            "y": round(sy, 2),
                            "z": round(sz, 2)
                        }
                    })

                    del spaces[i]
                    spaces.append((sx + p_len, sy, sz, sl - p_len, sb, sh))  # Right
                    spaces.append((sx, sy + p_br, sz, p_len, sb - p_br, sh))  # Front
                    spaces.append((sx, sy, sz + p_ht, p_len, p_br, sh - p_ht))  # Top

                    placed = True
                    break
            if placed:
                break
    return spaces, packed_items

def pack_products(vehicle: Dict[str, float], products: List[Dict]) -> List[Dict]:
    v_length, v_breadth, v_height = vehicle["length"], vehicle["breadth"], vehicle["height"]

    products = preprocess_products(products)

    # Group products by fragility levels
    bottom_products = [p for p in products if 1 <= p["fragility_index"] <= 4]
    middle_products = [p for p in products if 5 <= p["fragility_index"] <= 7]
    top_products = [p for p in products if 8 <= p["fragility_index"] <= 10]

    # Sort each group by volume descending
    bottom_products.sort(key=compute_volume, reverse=True)
    middle_products.sort(key=compute_volume, reverse=True)
    top_products.sort(key=compute_volume, reverse=True)

    packed_items = []
    spaces = [(0, 0, 0, v_length, v_breadth, v_height)]

    for group in [bottom_products, middle_products, top_products]:
        spaces, packed_items = pack_grouped_products(group, spaces, packed_items)

    return packed_items

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
    print(f"Total packed items: {len(packed)}")
    return {"packed_items": packed}
