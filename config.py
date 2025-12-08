"""OpenRouter API configuration for LangGraph agent."""
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.1-70b-instruct"

ALLOWED_CATEGORIES = ["fashion", "electronics", "home", "beauty", "sports", "food", "books", "other"]
ALLOWED_CONDITIONS = ["new", "used", "refurbished"]
