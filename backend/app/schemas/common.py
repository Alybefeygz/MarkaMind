from pydantic import BaseModel, ConfigDict, Field
from typing import List, Any, Optional, Generic, TypeVar

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(10, ge=1, le=100, description="Page size")
    sort: Optional[str] = Field("created_at", description="Sort field")
    
    model_config = ConfigDict(from_attributes=True)


class PaginationResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses"""
    items: List[T]
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    model_config = ConfigDict(from_attributes=True)


class StatusResponse(BaseModel):
    """Schema for status/success responses"""
    success: bool
    message: str
    data: Optional[Any] = None
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: bool = True
    message: str
    details: Optional[str] = None
    code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Schema for file upload responses"""
    success: bool
    filename: str
    url: str
    size: int
    mime_type: str
    
    model_config = ConfigDict(from_attributes=True)