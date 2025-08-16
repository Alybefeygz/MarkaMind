from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from uuid import UUID
import os
import uuid
import mimetypes
from pathlib import Path

from ..schemas.common import FileUploadResponse, StatusResponse, PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client

router = APIRouter(
    prefix="/uploads",
    tags=["File Uploads"],
    responses={404: {"description": "Not found"}}
)

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx", ".md", ".json", ".csv"}
ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/pdf", 
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown",
    "application/json",
    "text/csv"
}


def ensure_upload_dir():
    """Create upload directory if it doesn't exist"""
    upload_path = Path(UPLOAD_DIR)
    upload_path.mkdir(exist_ok=True)
    return upload_path


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file size
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    if file.filename:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{file_ext}' not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MIME type '{file.content_type}' not allowed"
        )


@router.post("/", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    chatbot_id: UUID = Form(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Upload a file for a chatbot
    """
    try:
        # Verify chatbot belongs to user
        chatbot_result = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )
        
        # Validate file
        validate_file(file)
        
        # Ensure upload directory exists
        upload_path = ensure_upload_dir()
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_path / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Get file size
        file_size = len(content)
        
        # Store file info in database
        upload_data = {
            "chatbot_id": str(chatbot_id),
            "file_name": file.filename or unique_filename,
            "file_type": file.content_type,
            "storage_url": str(file_path),
            "processed": False
        }
        
        result = supabase.table("uploads").insert(upload_data).execute()
        
        if not result.data:
            # Clean up file if database insert failed
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to store file information"
            )
        
        return FileUploadResponse(
            success=True,
            filename=file.filename or unique_filename,
            url=str(file_path),
            size=file_size,
            mime_type=file.content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    finally:
        # Close file if still open
        if not file.file.closed:
            await file.close()


@router.get("/", response_model=PaginationResponse[dict])
async def list_uploads(
    pagination: PaginationParams = Depends(),
    chatbot_id: Optional[UUID] = None,
    processed: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of uploaded files with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query - join with chatbots and brands to ensure user ownership
        query = supabase.table("uploads").select(
            "id, file_name, file_type, processed, created_at, chatbots!inner(brands!inner(user_id))",
            count="exact"
        ).eq("chatbots.brands.user_id", current_user["id"])
        
        # Apply filters
        if chatbot_id:
            query = query.eq("chatbot_id", str(chatbot_id))
        
        if processed is not None:
            query = query.eq("processed", processed)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0
        
        # Get uploads with pagination
        query = query.order(pagination.sort or "created_at", desc=True).range(offset, offset + pagination.size - 1)
        result = query.execute()
        
        # Process results to exclude nested fields from response
        uploads = []
        if result.data:
            for item in result.data:
                # Remove the nested fields before creating response
                upload_data = {k: v for k, v in item.items() if k != "chatbots"}
                uploads.append(upload_data)
        
        return PaginationResponse(
            items=uploads,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get uploads: {str(e)}"
        )


@router.get("/{upload_id}")
async def get_upload(
    upload_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific upload by ID
    """
    try:
        # Get upload with ownership check
        result = supabase.table("uploads").select(
            "*, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(upload_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        # Remove nested fields from response
        upload_data = {k: v for k, v in result.data[0].items() if k != "chatbots"}
        return upload_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upload: {str(e)}"
        )


@router.delete("/{upload_id}", response_model=StatusResponse)
async def delete_upload(
    upload_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific upload
    """
    try:
        # Get upload with ownership check
        upload_result = supabase.table("uploads").select(
            "id, file_name, storage_url, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(upload_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not upload_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        upload_info = upload_result.data[0]
        
        # Delete from database
        result = supabase.table("uploads").delete().eq("id", str(upload_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete upload"
            )
        
        # Try to delete physical file
        try:
            file_path = Path(upload_info["storage_url"])
            if file_path.exists():
                os.remove(file_path)
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Warning: Failed to delete physical file: {e}")
        
        return StatusResponse(
            success=True,
            message="Upload deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete upload: {str(e)}"
        )


@router.patch("/{upload_id}/process", response_model=StatusResponse)
async def mark_upload_processed(
    upload_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Mark an upload as processed
    """
    try:
        # Check if upload exists and user owns it
        existing = supabase.table("uploads").select(
            "id, processed, chatbots!inner(brands!inner(user_id))"
        ).eq("id", str(upload_id)).eq("chatbots.brands.user_id", current_user["id"]).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        current_processed = existing.data[0].get("processed")
        
        if current_processed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Upload is already marked as processed"
            )
        
        # Update processed status
        result = supabase.table("uploads").update({
            "processed": True
        }).eq("id", str(upload_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update upload status"
            )
        
        return StatusResponse(
            success=True,
            message="Upload marked as processed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )


@router.post("/batch-upload", response_model=List[FileUploadResponse])
async def batch_upload_files(
    files: List[UploadFile] = File(...),
    chatbot_id: UUID = Form(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Upload multiple files for a chatbot
    """
    try:
        # Verify chatbot belongs to user
        chatbot_result = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )
        
        if len(files) > 10:  # Limit batch uploads
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per batch upload"
            )
        
        # Ensure upload directory exists
        upload_path = ensure_upload_dir()
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                # Validate file
                validate_file(file)
                
                # Generate unique filename
                file_ext = Path(file.filename).suffix if file.filename else ""
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = upload_path / unique_filename
                
                # Save file
                content = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                
                # Get file size
                file_size = len(content)
                
                # Store file info in database
                upload_data = {
                    "chatbot_id": str(chatbot_id),
                    "file_name": file.filename or unique_filename,
                    "file_type": file.content_type,
                    "storage_url": str(file_path),
                    "processed": False
                }
                
                result = supabase.table("uploads").insert(upload_data).execute()
                
                if result.data:
                    uploaded_files.append(FileUploadResponse(
                        success=True,
                        filename=file.filename or unique_filename,
                        url=str(file_path),
                        size=file_size,
                        mime_type=file.content_type
                    ))
                else:
                    # Clean up file if database insert failed
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    failed_files.append(file.filename or "unknown")
                
            except Exception as e:
                failed_files.append(f"{file.filename or 'unknown'}: {str(e)}")
            finally:
                # Close file if still open
                if not file.file.closed:
                    await file.close()
        
        if failed_files:
            # Return partial success with error details
            raise HTTPException(
                status_code=status.HTTP_207_MULTI_STATUS,
                detail={
                    "message": f"Uploaded {len(uploaded_files)} files successfully, {len(failed_files)} failed",
                    "uploaded": uploaded_files,
                    "failed": failed_files
                }
            )
        
        return uploaded_files
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch upload files: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}/stats")
async def get_chatbot_upload_stats(
    chatbot_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get upload statistics for a specific chatbot
    """
    try:
        # Verify chatbot belongs to user
        chatbot_result = supabase.table("chatbots").select(
            "id, brands!inner(user_id)"
        ).eq("id", str(chatbot_id)).eq("brands.user_id", current_user["id"]).execute()
        
        if not chatbot_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or not owned by user"
            )
        
        # Get upload statistics
        result = supabase.table("uploads").select(
            "processed, file_type"
        ).eq("chatbot_id", str(chatbot_id)).execute()
        
        if not result.data:
            return {
                "total_uploads": 0,
                "processed_count": 0,
                "pending_count": 0,
                "file_types": {}
            }
        
        # Calculate statistics
        total_uploads = len(result.data)
        processed_count = sum(1 for upload in result.data if upload.get("processed"))
        pending_count = total_uploads - processed_count
        
        # Count by file type
        file_types = {}
        for upload in result.data:
            file_type = upload.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            "total_uploads": total_uploads,
            "processed_count": processed_count,
            "pending_count": pending_count,
            "file_types": file_types
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upload stats: {str(e)}"
        )