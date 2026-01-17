"""Document Service

Business logic for document management.
"""

from typing import Optional, Tuple, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import boto3
from botocore.config import Config

from app.models.document import Document, DocumentType, DocumentStatus
from app.core.config import settings


class DocumentService:
    """Service for document management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._s3_client = None
    
    @property
    def s3_client(self):
        """Get S3 client."""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=Config(signature_version='s3v4')
            )
        return self._s3_client
    
    async def create_upload_url(
        self,
        claim_id: UUID,
        document_type: DocumentType,
        description: Optional[str],
        uploaded_by: UUID
    ) -> dict:
        """Create presigned URL for document upload."""
        # Create document record
        document_id = uuid4()
        file_key = f"claims/{claim_id}/{document_id}"
        
        document = Document(
            id=document_id,
            claim_id=claim_id,
            document_type=document_type,
            description=description,
            original_filename="pending",
            file_reference=file_key,
            file_type="pending",
            file_size=0,
            status=DocumentStatus.PENDING,
            uploaded_by=uploaded_by,
        )
        
        self.db.add(document)
        await self.db.flush()
        
        # Generate presigned URL
        presigned_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': file_key,
                'ContentType': 'application/octet-stream',
            },
            ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRY
        )
        
        return {
            "document_id": document_id,
            "upload_url": presigned_url,
            "expires_in": settings.S3_PRESIGNED_URL_EXPIRY,
            "max_size_bytes": settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024,
            "allowed_content_types": settings.ALLOWED_FILE_TYPES
        }
    
    async def confirm_upload(
        self,
        document_id: UUID,
        filename: str,
        file_size: int,
        content_type: str,
        checksum: Optional[str] = None
    ) -> Optional[Document]:
        """Confirm document upload completion."""
        document = await self.get_by_id(document_id)
        
        if not document:
            return None
        
        # Validate content type
        if content_type not in settings.ALLOWED_FILE_TYPES:
            document.status = DocumentStatus.REJECTED
            await self.db.flush()
            raise ValueError(f"Invalid content type: {content_type}")
        
        # Validate file size
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            document.status = DocumentStatus.REJECTED
            await self.db.flush()
            raise ValueError(f"File too large: {file_size} bytes")
        
        # Update document record
        document.original_filename = filename
        document.file_type = content_type
        document.file_size = file_size
        document.checksum = checksum
        document.status = DocumentStatus.UPLOADED
        document.uploaded_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(document)
        
        # TODO: Trigger virus scan
        
        return document
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_download_url(self, document_id: UUID) -> Optional[dict]:
        """Get document with download URL."""
        document = await self.get_by_id(document_id)
        
        if not document:
            return None
        
        # Generate presigned download URL
        download_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': document.file_reference,
                'ResponseContentDisposition': f'attachment; filename="{document.original_filename}"'
            },
            ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRY
        )
        
        # Convert to dict and add URL
        doc_dict = {
            "id": document.id,
            "claim_id": document.claim_id,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "document_type": document.document_type,
            "description": document.description,
            "status": document.status,
            "uploaded_at": document.uploaded_at,
            "created_at": document.created_at,
            "checksum": document.checksum,
            "virus_scan_result": document.virus_scan_result,
            "download_url": download_url,
            "download_url_expires": datetime.utcnow() + timedelta(seconds=settings.S3_PRESIGNED_URL_EXPIRY)
        }
        
        return doc_dict
    
    async def list(
        self,
        claim_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Document], int]:
        """List documents with filtering and pagination."""
        query = select(Document).where(Document.status != DocumentStatus.DELETED)
        count_query = select(func.count(Document.id)).where(Document.status != DocumentStatus.DELETED)
        
        if claim_id:
            query = query.where(Document.claim_id == claim_id)
            count_query = count_query.where(Document.claim_id == claim_id)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(Document.created_at.desc())
        
        result = await self.db.execute(query)
        documents = result.scalars().all()
        
        return list(documents), total
    
    async def delete(self, document_id: UUID) -> bool:
        """Soft delete document."""
        document = await self.get_by_id(document_id)
        
        if not document:
            return False
        
        document.status = DocumentStatus.DELETED
        await self.db.flush()
        
        # TODO: Schedule S3 object deletion
        
        return True
