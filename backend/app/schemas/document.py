"""Document Schemas

Pydantic models for document management API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.schemas.common import BaseSchema, PaginationMeta
from app.models.document import DocumentType, DocumentStatus


class DocumentUpload(BaseModel):
    """Schema for document upload request."""
    claim_id: UUID
    document_type: DocumentType = DocumentType.OTHER
    description: Optional[str] = Field(None, max_length=500)


class DocumentUploadResponse(BaseModel):
    """Response with presigned upload URL."""
    document_id: UUID
    upload_url: str
    expires_in: int
    max_size_bytes: int
    allowed_content_types: List[str]


class DocumentResponse(BaseSchema):
    """Document response schema."""
    id: UUID
    claim_id: UUID
    original_filename: str
    file_type: str
    file_size: int
    document_type: DocumentType
    description: Optional[str]
    status: DocumentStatus
    uploaded_at: Optional[datetime]
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response with download URL."""
    download_url: Optional[str] = None
    download_url_expires: Optional[datetime] = None
    checksum: Optional[str] = None
    virus_scan_result: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Paginated document list response."""
    data: List[DocumentResponse]
    meta: PaginationMeta


class DocumentConfirmUpload(BaseModel):
    """Confirm document upload completion."""
    filename: str
    file_size: int
    content_type: str
    checksum: Optional[str] = None
