"""Pydantic models for WhatsApp webhook payloads."""
from pydantic import BaseModel, Field
from typing import Optional, List


class TextMessage(BaseModel):
    body: str


class ImageMessage(BaseModel):
    id: str
    mime_type: str
    caption: Optional[str] = None


class Profile(BaseModel):
    name: str


class Contact(BaseModel):
    profile: Profile
    wa_id: str


class Message(BaseModel):
    from_: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[TextMessage] = None
    image: Optional[ImageMessage] = None


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: Optional[List[dict]] = None  # Ignore statuses


class Change(BaseModel):
    value: Value
    field: str


class Entry(BaseModel):
    id: str
    changes: List[Change]


class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[Entry]