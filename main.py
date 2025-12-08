"""FastAPI webhook server for WhatsApp Business API integration."""
import logging
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import os

from models import WhatsAppWebhook
from whatsapp_service import WhatsAppService
from session_service import SessionService
from storage_service import StorageService
from agent import chat, create_initial_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp Bot Service")

# Initialize services
whatsapp_service = WhatsAppService(
    access_token=os.getenv("WHATSAPP_ACCESS_TOKEN"),
    phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID")
)
session_service = SessionService(redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"))
storage_service = StorageService(
    bucket_name=os.getenv("S3_BUCKET_NAME"),
    region=os.getenv("S3_REGION", "us-east-1")
)


@app.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    """Verify webhook for Meta WhatsApp setup."""
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=hub_challenge)
    
    logger.warning(f"Webhook verification failed. Token mismatch.")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp")
async def webhook_handler(request: Request):
    """Handle incoming WhatsApp messages."""
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Parse webhook data
        webhook_data = WhatsAppWebhook(**body)
        
        # Process each entry
        for entry in webhook_data.entry:
            for change in entry.changes:
                # Ignore status updates
                if not change.value.messages:
                    logger.info("Ignoring status update")
                    continue
                
                # Process each message
                for message in change.value.messages:
                    await process_message(message, change.value.contacts[0].wa_id)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Return 200 to prevent WhatsApp retries
        return {"status": "error", "message": str(e)}


async def process_message(message, sender_phone: str):
    """Process a single WhatsApp message."""
    try:
        logger.info(f"Processing message from {sender_phone}, type: {message.type}")
        
        message_text = ""
        image_urls = []
        
        # Extract text
        if message.type == "text":
            message_text = message.text.body
        elif message.type == "image":
            # Handle image with optional caption
            if message.image.caption:
                message_text = message.image.caption
            
            # Download and upload image
            try:
                media_id = message.image.id
                logger.info(f"Downloading image with media_id: {media_id}")
                
                image_bytes = await whatsapp_service.download_media(media_id)
                image_url = await storage_service.upload_image(
                    image_bytes,
                    f"{sender_phone}_{message.id}.jpg"
                )
                image_urls.append(image_url)
                logger.info(f"Image uploaded to: {image_url}")
            except Exception as e:
                logger.error(f"Image processing failed: {e}")
                message_text += "\n[Note: Image upload failed, but I'll help you anyway]"
        else:
            logger.info(f"Unsupported message type: {message.type}")
            await whatsapp_service.send_message(
                sender_phone,
                "Sorry, I can only process text and images for now."
            )
            return
        
        # Load or create session
        try:
            state = await session_service.get_state(sender_phone)
            if state is None:
                logger.info(f"Creating new session for {sender_phone}")
                state = create_initial_state(sender_phone)
        except Exception as e:
            logger.warning(f"Redis failed, creating temporary session: {e}")
            state = create_initial_state(sender_phone)
        
        # Call agent
        try:
            logger.info(f"Calling agent with message: {message_text[:50]}...")
            new_state = chat(state, message_text, image_urls if image_urls else None)
        except Exception as e:
            logger.error(f"Agent failed: {e}", exc_info=True)
            await whatsapp_service.send_message(
                sender_phone,
                "Sorry, I'm having trouble processing that. Can you try again?"
            )
            return
        
        # Extract response
        response_text = None
        for msg in reversed(new_state["messages"]):
            if msg["role"] == "assistant":
                response_text = msg["content"]
                break
        
        if not response_text:
            response_text = "I'm here to help! What would you like to do?"
        
        # Handle length constraints (WhatsApp limit: 4096 chars)
        if len(response_text) > 4096:
            response_text = response_text[:4090] + "... (message truncated)"
        
        # Save state
        try:
            await session_service.save_state(sender_phone, new_state)
        except Exception as e:
            logger.warning(f"Failed to save state to Redis: {e}")
        
        # Send response
        await whatsapp_service.send_message(sender_phone, response_text)
        logger.info(f"Response sent to {sender_phone}")
    
    except Exception as e:
        logger.error(f"Error in process_message: {e}", exc_info=True)
        # Try to send error message to user
        try:
            await whatsapp_service.send_message(
                sender_phone,
                "Sorry, something went wrong. Please try again."
            )
        except:
            pass


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)