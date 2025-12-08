"""Test script for simulating WhatsApp webhook requests."""
import httpx
import asyncio
import json


# Test payloads
TEXT_MESSAGE_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "123456789",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "1234567890",
                    "phone_number_id": "test_phone_id"
                },
                "contacts": [{
                    "profile": {"name": "Test User"},
                    "wa_id": "2348012345678"
                }],
                "messages": [{
                    "from": "2348012345678",
                    "id": "wamid.test123",
                    "timestamp": "1702901234",
                    "type": "text",
                    "text": {"body": "I want to add Nike shoes for 20000 naira"}
                }]
            },
            "field": "messages"
        }]
    }]
}

STATUS_UPDATE_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "123456789",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "1234567890",
                    "phone_number_id": "test_phone_id"
                },
                "statuses": [{
                    "id": "wamid.test123",
                    "status": "delivered",
                    "timestamp": "1702901236"
                }]
            },
            "field": "messages"
        }]
    }]
}


async def test_webhook_verification():
    """Test webhook verification (GET request)."""
    print("\n=== Testing Webhook Verification ===")
    url = "http://localhost:8000/webhook/whatsapp"
    params = {
        "hub.mode": "subscribe",
        "hub.challenge": "test_challenge_123",
        "hub.verify_token": "your_custom_verify_token_here"  # Match .env
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            assert response.status_code == 200
            assert response.text == "test_challenge_123"
            print("✅ Verification test passed")
        except Exception as e:
            print(f"❌ Verification test failed: {e}")


async def test_text_message():
    """Test text message webhook."""
    print("\n=== Testing Text Message ===")
    url = "http://localhost:8000/webhook/whatsapp"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=TEXT_MESSAGE_PAYLOAD)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            print("✅ Text message test passed")
        except Exception as e:
            print(f"❌ Text message test failed: {e}")


async def test_status_update():
    """Test that status updates are ignored."""
    print("\n=== Testing Status Update (Should be Ignored) ===")
    url = "http://localhost:8000/webhook/whatsapp"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=STATUS_UPDATE_PAYLOAD)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            print("✅ Status update correctly ignored")
        except Exception as e:
            print(f"❌ Status update test failed: {e}")


async def run_all_tests():
    """Run all tests."""
    print("🧪 Starting WhatsApp Webhook Tests")
    print("=" * 50)
    print("Make sure the server is running: uvicorn main:app --reload")
    print("=" * 50)
    
    await test_webhook_verification()
    await test_text_message()
    await test_status_update()
    
    print("\n" + "=" * 50)
    print("✅ All basic tests completed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())