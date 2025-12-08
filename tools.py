"""Mock tool implementations for inventory management."""
from typing import Optional
from config import ALLOWED_CATEGORIES, ALLOWED_CONDITIONS


def validate_product_data(data: dict) -> tuple[bool, str]:
    """Validate product data before creation/update."""
    if "price" in data and (not isinstance(data["price"], (int, float)) or data["price"] <= 0):
        return False, "Price must be greater than 0"
    if "quantity" in data and (not isinstance(data["quantity"], int) or data["quantity"] < 0):
        return False, "Quantity must be 0 or greater"
    if "category" in data and data["category"].lower() not in ALLOWED_CATEGORIES:
        return False, f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}"
    if "condition" in data and data["condition"].lower() not in ALLOWED_CONDITIONS:
        return False, f"Condition must be one of: {', '.join(ALLOWED_CONDITIONS)}"
    return True, ""


def create_product(
    title: str,
    price: float,
    category: str,
    quantity: int,
    condition: str,
    description: Optional[str] = None,
    size: Optional[str] = None,
    brand: Optional[str] = None,
    image_urls: Optional[list[str]] = None
) -> dict:
    """Create a new product listing. Returns mock success response."""
    data = {"title": title, "price": price, "category": category, "quantity": quantity, "condition": condition}
    valid, error = validate_product_data(data)
    if not valid:
        return {"success": False, "error": error}
    
    product_id = f"PROD_{hash(title) % 10000:04d}"
    print(f"[MOCK] Creating product: {title} | ₦{price:,.0f} | {category} | qty: {quantity}")
    return {"success": True, "product_id": product_id, "message": f"Product '{title}' created successfully"}


def query_inventory(search_term: str) -> dict:
    """Search inventory by term. Returns mock results."""
    print(f"[MOCK] Searching inventory for: {search_term}")
    return {
        "success": True,
        "results": [
            {"product_id": "PROD_0001", "title": f"Sample {search_term}", "price": 15000, "quantity": 5},
            {"product_id": "PROD_0002", "title": f"Premium {search_term}", "price": 25000, "quantity": 3}
        ],
        "total": 2
    }


def update_product(product_id: str, updates: dict) -> dict:
    """Update an existing product. Returns mock success."""
    valid, error = validate_product_data(updates)
    if not valid:
        return {"success": False, "error": error}
    
    print(f"[MOCK] Updating product {product_id}: {updates}")
    return {"success": True, "product_id": product_id, "message": "Product updated successfully"}


def list_products(limit: int = 10) -> dict:
    """List seller's products. Returns mock data."""
    print(f"[MOCK] Listing up to {limit} products")
    return {
        "success": True,
        "products": [
            {"product_id": "PROD_0001", "title": "Nike Air Max", "price": 45000, "quantity": 2, "category": "sports"},
            {"product_id": "PROD_0002", "title": "iPhone Case", "price": 5000, "quantity": 15, "category": "electronics"}
        ][:limit],
        "total": 2
    }
