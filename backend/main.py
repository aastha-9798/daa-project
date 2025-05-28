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

def get_padding_factor(fragility_index: int, weight: int) -> float:
    return 1 + (0.02 * fragility_index  + 0.005 * weight ) 

def generate_rotations(length: float, breadth: float, height: float):
    return set(itertools.permutations([length, breadth, height]))

def compute_volume(p: Dict) -> float:
    return p["padded_length"] * p["padded_breadth"] * p["padded_height"]

def preprocess_products(products: List[Dict]) -> List[Dict]:
    for product in products:
        factor = get_padding_factor(product["fragility_index"] , product["weight"], (product["length"] * product["breadth"]*product["height"]))
        product["padded_length"] = product["length"] * factor
        product["padded_breadth"] = product["breadth"] * factor
        product["padded_height"] = product["height"] * factor
    return products

def pack_grouped_products(products_group: List[Dict], spacesR: List[tuple],spacesT: List[tuple],spacesF: List[tuple], packed_items: List[Dict]):
    for product in products_group:
        placed = False
        rotations = generate_rotations(product["padded_length"], product["padded_breadth"], product["padded_height"])
        for i in range(len(spacesR)):
            sx, sy, sz, sl, sb, sh = spacesR[i]
            for rot in rotations:
                p_len, p_br, p_ht = rot
                if p_len <= sl and p_br <= sb and p_ht <= sh:
                    packed_items.append({
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "fragility_index": product["fragility_index"],
                        "distance":product["distance"],
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

                    del spacesR[i]
                    spacesT.append((sx, sy, sz + p_ht, p_len, p_br, sh - p_ht))  # Top
                    spacesF.append((sx, sy + p_br, sz, p_len, sb - p_br, sh))  # Front
                    spacesR.append((sx + p_len, sy, sz, sl - p_len, sb, sh))  # Right
                    placed = True
                    break
                if placed :
                    break
        if not placed: 
            for i in range(len(spacesT)):
                sx, sy, sz, sl, sb, sh = spacesT[i]
                for rot in rotations:
                    p_len, p_br, p_ht = rot
                    if p_len <= sl and p_br <= sb and p_ht <= sh:
                        packed_items.append({
                            "product_id": product["product_id"],
                            "product_name": product["product_name"],
                            "fragility_index": product["fragility_index"],
                            "distance":product["distance"],
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

                        del spacesT[i]
                        spacesT.append((sx, sy, sz + p_ht, p_len, p_br, sh - p_ht))  # Top
                        spacesF.append((sx, sy + p_br, sz, p_len, sb - p_br, sh))  # Front
                        spacesR.append((sx + p_len, sy, sz, sl - p_len, sb, sh))  # Right
                        placed = True
                        break
                if placed :
                    break
        if not placed:
            for i in range(len(spacesF)):
                sx, sy, sz, sl, sb, sh = spacesF[i]
                for rot in rotations:
                    p_len, p_br, p_ht = rot
                    if p_len <= sl and p_br <= sb and p_ht <= sh:
                        packed_items.append({
                            "product_id": product["product_id"],
                            "product_name": product["product_name"],
                            "fragility_index": product["fragility_index"],
                            "distance":product["distance"],
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

                        del spacesF[i]
                        spacesT.append((sx, sy, sz + p_ht, p_len, p_br, sh - p_ht))  # Top
                        spacesF.append((sx, sy + p_br, sz, p_len, sb - p_br, sh))  # Front
                        spacesR.append((sx + p_len, sy, sz, sl - p_len, sb, sh))  # Right
                        placed = True
                        break
                if placed :
                    break

    print("spaceR : " , len(spacesR))
    print("spaceT : " , len(spacesT))
    print("spaceF : " , len(spacesF))
    print("s0: " , spacesF[0])
    return packed_items

def pack_products(vehicle: Dict[str, float], products: List[Dict]) -> List[Dict]:
    v_length, v_breadth, v_height = vehicle["length"], vehicle["breadth"], vehicle["height"]

    # Step 1: Preprocess with padding
    products = preprocess_products(products)

    # Step 2: Sort by distance descending
    products.sort(key=lambda p: p["distance"], reverse=True)

    # Step 3: Divide into 5 batches
    batch_size = len(products) // 5
    remainder = len(products) % 5
    batches = []
    start = 0
    for i in range(5):
        end = start + batch_size + (1 if i < remainder else 0)
        batches.append(products[start:end])
        start = end

    # Step 4: Sort each batch by volume
    for batch in batches:
        batch.sort(key=compute_volume, reverse=True)

    # Step 5: Merge batches in order
    merged_products = list(itertools.chain(*batches))

    # Step 6: Pack all merged products
    packed_items = []
    spacesR = [(0, 0, 0, v_length, v_breadth, v_height)]
    spacesT = []
    spacesF = []
    packed_items = pack_grouped_products(merged_products, spacesR,spacesT,spacesF, packed_items)

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
