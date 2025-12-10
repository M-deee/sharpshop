"""Supabase-backed tool implementations for inventory management."""
from typing import Optional
from config import ALLOWED_CATEGORIES, ALLOWED_CONDITIONS
from database import get_supabase

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
    seller_id: str,
    description: Optional[str] = None,
    size: Optional[str] = None,
    brand: Optional[str] = None,
    image_urls: Optional[list[str]] = None
) -> dict:
    """Create a new product listing in Supabase."""
    data = {"title": title, "price": price, "category": category, "quantity": quantity, "condition": condition}
    valid, error = validate_product_data(data)
    if not valid:
        return {"success": False, "error": error}
    
    supabase = get_supabase()
    
    product_data = {
        "seller_id": seller_id,
        "title": title,
        "price": price,
        "category": category.lower(),
        "quantity": quantity,
        "condition": condition.lower(),
        "description": description,
        "size": size,
        "brand": brand,
        "image_urls": image_urls or []
    }
    
    try:
        result = supabase.table("products").insert(product_data).execute()
        product = result.data[0]
        return {
            "success": True,
            "product_id": product["id"],
            "message": f"Product '{title}' created successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def query_inventory(search_term: str, seller_id: str) -> dict:
    """Search inventory by term."""
    supabase = get_supabase()
    
    try:
        query = supabase.table("products").select("*").eq("seller_id", seller_id)
        
        if search_term:
            query = query.ilike("title", f"%{search_term}%")
        
        result = query.execute()
        
        return {
            "success": True,
            "results": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "results": [], "total": 0}


def update_product(product_id: str, updates: dict, seller_id: str) -> dict:
    """Update an existing product."""
    valid, error = validate_product_data(updates)
    if not valid:
        return {"success": False, "error": error}
    
    supabase = get_supabase()
    
    try:
        # Check if product belongs to seller
        check = supabase.table("products").select("id").eq("id", product_id).eq("seller_id", seller_id).execute()
        
        if not check.data:
            return {"success": False, "error": "Product not found or you don't have permission"}
        
        result = supabase.table("products").update(updates).eq("id", product_id).execute()
        
        return {
            "success": True,
            "product_id": product_id,
            "message": "Product updated successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_products(seller_id: str, limit: int = 10) -> dict:
    """List seller's products."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("products").select("*").eq("seller_id", seller_id).limit(limit).execute()
        
        return {
            "success": True,
            "products": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "products": [], "total": 0}