"""WhatsApp Business API client for sending messages and downloading media."""
import httpx
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for interacting with Meta WhatsApp Cloud API."""
    
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, to: str, text: str) -> dict:
        """Send a text message to a WhatsApp user."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": text}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Message sent successfully to {to}")
                return result
            except httpx.HTTPError as e:
                logger.error(f"Failed to send message to {to}: {e}")
                raise
    
    async def download_media(self, media_id: str) -> bytes:
        """Download media file from WhatsApp."""
        # Step 1: Get media URL
        url = f"{self.base_url}/{media_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                # Get media URL
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                media_data = response.json()
                media_url = media_data.get("url")
                
                if not media_url:
                    raise ValueError("No URL in media response")
                
                logger.info(f"Got media URL for {media_id}")
                
                # Step 2: Download actual media
                media_response = await client.get(
                    media_url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=60.0
                )
                media_response.raise_for_status()
                
                logger.info(f"Downloaded media {media_id}, size: {len(media_response.content)} bytes")
                return media_response.content
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to download media {media_id}: {e}")
                raise