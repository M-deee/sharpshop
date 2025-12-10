"""Supabase database operations."""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Optional

def get_supabase() -> Client:
    """Get Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_seller(phone_number: str, name: str = "Seller") -> dict:
    """Get existing seller or create new one."""
    supabase = get_supabase()
    
    # Try to get existing seller
    result = supabase.table("sellers").select("*").eq("phone_number", phone_number).execute()
    
    if result.data:
        return result.data[0]
    
    # Create new seller
    new_seller = supabase.table("sellers").insert({
        "phone_number": phone_number,
        "name": name
    }).execute()
    
    return new_seller.data[0]