"""S3 service for uploading and storing images."""
import boto3
import logging
from typing import Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class StorageService:
    """Service for uploading images to S3."""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    async def upload_image(self, image_bytes: bytes, filename: str) -> str:
        """Upload image to S3 and return public URL."""
        try:
            # Generate unique key with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            key = f"whatsapp_images/{timestamp}_{filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType='image/jpeg',
                ACL='public-read'  # Make image publicly accessible
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            logger.info(f"Uploaded image to S3: {url}")
            return url
        
        except Exception as e:
            logger.error(f"Failed to upload image to S3: {e}")
            raise
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for private objects (alternative approach)."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise