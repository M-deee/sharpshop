"""FastAPI server for WhatsApp chatbot."""
from fastapi import FastAPI, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from agent import create_initial_state, chat
from database import get_or_create_seller
from storage import process_images  # NEW IMPORT
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    force=True
)

app = FastAPI()

# In-memory session store
user_sessions = {}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages."""
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    sender_id = form_data.get('From', '')
    
    # Check for media (images)
    num_media = int(form_data.get('NumMedia', 0))
    twilio_image_urls = []
    if num_media > 0:
        for i in range(num_media):
            media_url = form_data.get(f'MediaUrl{i}')
            if media_url:
                twilio_image_urls.append(media_url)
    
    logging.info(f"Received message from {sender_id}: {incoming_msg}")
    
    # Process images - download from Twilio and upload to Supabase
    permanent_image_urls = []
    if twilio_image_urls:
        logging.info(f"Processing {len(twilio_image_urls)} images...")
        permanent_image_urls = process_images(twilio_image_urls)
        logging.info(f"Uploaded {len(permanent_image_urls)} images to Supabase")

    # Get or create seller in database
    seller = get_or_create_seller(sender_id)
    seller_uuid = seller["id"]

    # Get or create user state
    if sender_id not in user_sessions:
        user_sessions[sender_id] = create_initial_state(seller_id=seller_uuid)
    
    state = user_sessions[sender_id]
    
    # Process message through agent
    try:
        new_state = chat(state, incoming_msg, permanent_image_urls)  # Pass permanent URLs
        user_sessions[sender_id] = new_state
        
        # Get the last assistant message
        response_text = "Sorry, I didn't understand that."
        for msg in reversed(new_state["messages"]):
            if msg["role"] == "assistant":
                response_text = msg["content"]
                break
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        response_text = "Sorry, I encountered an error processing your request."

    # Send response back to Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    
    return Response(content=str(resp), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)