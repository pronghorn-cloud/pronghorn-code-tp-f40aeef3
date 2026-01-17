"""Document Endpoints

Handles document upload and retrieval for claims.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.document import (
    DocumentUpload,
    DocumentResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentUploadResponse,
    DocumentConfirmUpload,
)
from app.schemas.common import SuccessResponse, PaginationMeta
from app.services.document_service import DocumentService
from app.services.claim_service import ClaimService
from app.services.audit_service import AuditService
from app.models.audit import AuditAction
from app.models.user import UserRole
from app.models.claim import ClaimStatus

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def request_upload_url(
    upload_request: DocumentUpload,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request a presigned URL for document upload."""
    document_service = DocumentService(db)
    claim_service = ClaimService(db)
    
    # Verify claim exists and user has access
    claim = await claim_service.get_by_id(upload_request.claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    # Check access
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Check if claim accepts documents
    if claim.status not in [ClaimStatus.DRAFT, ClaimStatus.IN_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload documents to this claim"
        )
    
    # Generate upload URL
    upload_data = await document_service.create_upload_url(
        claim_id=upload_request.claim_id,
        document_type=upload_request.document_type,
        description=upload_request.description,
        uploaded_by=current_user.id
    )
    
    return upload_data


@router.post("/{document_id}/confirm", response_model=DocumentResponse)
async def confirm_upload(
    document_id: UUID,
    confirm_data: DocumentConfirmUpload,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm document upload completion."""
    document_service = DocumentService(db)
    audit_service = AuditService(db)
    
    # Get document
    document = await document_service.get_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Confirm upload
    confirmed_doc = await document_service.confirm_upload(
        document_id,
        filename=confirm_data.filename,
        file_size=confirm_data.file_size,
        content_type=confirm_data.content_type,
        checksum=confirm_data.checksum
    )
    
    # Log upload
    await audit_service.log(
        action=AuditAction.DOCUMENT_UPLOADED,
        user_id=current_user.id,
        claim_id=document.claim_id,
        document_id=document_id,
        metadata={"filename": confirm_data.filename}
    )
    
    return DocumentResponse.model_validate(confirmed_doc)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    claim_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List documents."""
    document_service = DocumentService(db)
    claim_service = ClaimService(db)
    
    # If claim_id provided, verify access
    if claim_id:
        claim = await claim_service.get_by_id(claim_id)
        
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        if current_user.role == UserRole.PROVIDER:
            if claim.provider_id != current_user.provider_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
    
    # Get documents
    documents, total = await document_service.list(
        claim_id=claim_id,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return DocumentListResponse(
        data=[DocumentResponse.model_validate(d) for d in documents],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document details with download URL."""
    document_service = DocumentService(db)
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    document = await document_service.get_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check access via claim
    claim = await claim_service.get_by_id(document.claim_id)
    
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Generate download URL
    document_with_url = await document_service.get_with_download_url(document_id)
    
    # Log download
    await audit_service.log(
        action=AuditAction.DOCUMENT_DOWNLOADED,
        user_id=current_user.id,
        claim_id=document.claim_id,
        document_id=document_id,
    )
    
    return DocumentDetailResponse.model_validate(document_with_url)


@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document."""
    document_service = DocumentService(db)
    claim_service = ClaimService(db)
    audit_service = AuditService(db)
    
    document = await document_service.get_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check access via claim
    claim = await claim_service.get_by_id(document.claim_id)
    
    if current_user.role == UserRole.PROVIDER:
        if claim.provider_id != current_user.provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Only allow deletion on draft claims
    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete documents from submitted claims"
        )
    
    # Delete document
    await document_service.delete(document_id)
    
    # Log deletion
    await audit_service.log(
        action=AuditAction.DOCUMENT_DELETED,
        user_id=current_user.id,
        claim_id=document.claim_id,
        document_id=document_id,
    )
    
    return SuccessResponse(message="Document deleted successfully")
