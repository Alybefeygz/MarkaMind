from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ProductBase(BaseModel):
    """Base schema for Product"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    stock_quantity: int = Field(0, ge=0)
    track_inventory: bool = True
    allow_backorder: bool = False
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field("draft", pattern="^(draft|active|archived)$")
    featured: bool = False
    tags: List[str] = Field(default_factory=list)
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=200)
    seo_data: Dict[str, Any] = Field(default_factory=dict)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    store_id: UUID
    initial_review_count: int = Field(0, ge=0, le=3, description="Number of mock reviews to create (0-3)")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v.lower()

    @field_validator('compare_at_price')
    @classmethod
    def validate_compare_price(cls, v, info):
        """Validate compare_at_price is greater than or equal to price"""
        if v is not None and 'price' in info.data:
            if v < info.data['price']:
                raise ValueError('compare_at_price must be greater than or equal to price')
        return v


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    allow_backorder: Optional[bool] = None
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    dimensions: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|archived)$")
    featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=200)
    seo_data: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: UUID
    store_id: UUID
    average_rating: Decimal = Field(0.00, ge=0, le=5)
    review_count: int = 0
    view_count: int = 0
    sales_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """Schema for product list item"""
    id: UUID
    store_id: UUID
    name: str
    slug: str
    price: Decimal
    compare_at_price: Optional[Decimal] = None
    category: str
    status: str
    featured: bool
    stock_quantity: int
    average_rating: Decimal = Field(0.00, ge=0, le=5)
    review_count: int = 0
    sales_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductPublic(BaseModel):
    """Schema for public product information"""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Decimal
    compare_at_price: Optional[Decimal] = None
    category: str
    subcategory: Optional[str] = None
    stock_quantity: int
    allow_backorder: bool
    weight: Optional[Decimal] = None
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    featured: bool
    tags: List[str] = Field(default_factory=list)
    average_rating: Decimal = Field(0.00, ge=0, le=5)
    review_count: int = 0
    view_count: int = 0
    sales_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Product Images Schemas
class ProductImageBase(BaseModel):
    """Base schema for Product Image"""
    image_url: str = Field(..., min_length=1)
    alt_text: Optional[str] = Field(None, max_length=200)
    display_order: int = Field(0, ge=0)
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    """Schema for creating a product image"""
    product_id: UUID


class ProductImageUpdate(BaseModel):
    """Schema for updating a product image"""
    image_url: Optional[str] = Field(None, min_length=1)
    alt_text: Optional[str] = Field(None, max_length=200)
    display_order: Optional[int] = Field(None, ge=0)
    is_primary: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ProductImageResponse(ProductImageBase):
    """Schema for product image response"""
    id: UUID
    product_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Product Reviews Schemas
class ProductReviewBase(BaseModel):
    """Base schema for Product Review"""
    reviewer_name: str = Field(..., min_length=1, max_length=100)
    reviewer_email: Optional[str] = Field(None, max_length=200)
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: str = Field(..., min_length=1)
    verified_purchase: bool = False


class ProductReviewCreate(ProductReviewBase):
    """Schema for creating a product review"""
    product_id: UUID


class ProductReviewUpdate(BaseModel):
    """Schema for updating a product review (admin only)"""
    status: Optional[str] = Field(None, pattern="^(pending|approved|rejected)$")
    helpful_count: Optional[int] = Field(None, ge=0)

    model_config = ConfigDict(from_attributes=True)


class ProductReviewResponse(ProductReviewBase):
    """Schema for product review response"""
    id: UUID
    product_id: UUID
    user_id: Optional[UUID] = None
    status: str
    helpful_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductWithImages(ProductResponse):
    """Schema for product with images"""
    images: List[ProductImageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductDetail(ProductResponse):
    """Schema for detailed product information"""
    images: List[ProductImageResponse] = Field(default_factory=list)
    reviews: List[ProductReviewResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)