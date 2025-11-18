from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any


class ChatboxBase(BaseModel):
    """Base Chatbox model with common fields"""
    # ZORUNLU ALANLAR
    name: str = Field(..., min_length=1, max_length=100, description="Chatbox ismi (zorunlu)")
    chatbox_title: str = Field(..., min_length=1, max_length=100, description="Chatbox başlık (zorunlu)")
    initial_message: str = Field(..., min_length=1, description="İlk mesaj (zorunlu)")

    # ZORUNLU Renk Ayarları - Kullanıcı mutlaka göndermeli
    primary_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Ana renk (zorunlu)")
    ai_message_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="AI mesaj rengi (zorunlu)")
    user_message_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Kullanıcı mesaj rengi (zorunlu)")
    ai_text_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="AI yazı rengi (zorunlu)")
    user_text_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Kullanıcı yazı rengi (zorunlu)")

    # ZORUNLU Buton Renkleri - Kullanıcı mutlaka göndermeli
    button_primary_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Buton ana renk (zorunlu)")
    button_border_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Buton çerçeve rengi (zorunlu)")
    button_icon_color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$', description="Buton sembol rengi (zorunlu)")

    # OPSİYONEL ALANLAR - Varsayılan değerlerle
    placeholder_text: str = Field("Mesajınızı yazın...", max_length=200, description="Placeholder text (opsiyonel)")
    avatar_url: Optional[str] = Field(None, description="Avatar URL (opsiyonel)")
    animation_style: str = Field("fade", pattern=r'^(fade|slide|bounce|none)$', description="Animasyon stili (opsiyonel)")
    language: str = Field("tr", pattern=r'^(tr|en|de|fr|es)$', description="Dil (opsiyonel)")
    status: str = Field("active", pattern=r'^(draft|active|inactive)$', description="Durum (opsiyonel - varsayılan: active)")


class ChatboxCreate(ChatboxBase):
    """Chatbox model for creation requests"""
    brand_id: Optional[UUID] = Field(None, description="Brand ID (opsiyonel)")
    store_id: Optional[UUID] = Field(None, description="Store ID (opsiyonel)")


class ChatboxUpdate(BaseModel):
    """Chatbox model for update requests - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    chatbox_title: Optional[str] = Field(None, min_length=1, max_length=100)
    initial_message: Optional[str] = Field(None, min_length=1)
    placeholder_text: Optional[str] = Field(None, max_length=200)

    # Renk Ayarları
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    ai_message_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    user_message_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    ai_text_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    user_text_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    # Buton Renkleri
    button_primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    button_border_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    button_icon_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    # İlişkiler
    brand_id: Optional[UUID] = Field(None, description="Brand ID")
    store_id: Optional[UUID] = Field(None, description="Store ID")

    # Diğer
    avatar_url: Optional[str] = None
    animation_style: Optional[str] = Field(None, pattern=r'^(fade|slide|bounce|none)$')
    language: Optional[str] = Field(None, pattern=r'^(tr|en|de|fr|es)$')
    status: Optional[str] = Field(None, pattern=r'^(draft|active|inactive)$')


class ChatboxList(BaseModel):
    """Schema for chatbox list view"""
    id: UUID
    name: str
    chatbox_title: str
    status: str
    created_at: datetime
    store_count: int = 0
    product_count: int = 0
    conversation_count: int = 0
    knowledge_source_count: int = 0

    # Buton Renkleri (badge'ler için gerekli)
    button_primary_color: str
    button_border_color: str
    button_icon_color: str
    primary_color: str  # Fallback için

    model_config = ConfigDict(from_attributes=True)


class StoreBasicInfo(BaseModel):
    """Basic store information for relations"""
    id: UUID
    name: str
    slug: str
    logo: Optional[str] = None


class ProductBasicInfo(BaseModel):
    """Basic product information for relations"""
    id: UUID
    name: str
    slug: str
    price: str
    category: str
    store_name: str


class ChatboxResponse(BaseModel):
    """Complete Chatbox response with all fields"""
    id: UUID
    brand_id: Optional[UUID] = None
    store_id: Optional[UUID] = None
    name: str
    chatbox_title: str
    initial_message: str
    placeholder_text: str

    # Renk Ayarları
    primary_color: str
    ai_message_color: str
    user_message_color: str
    ai_text_color: str
    user_text_color: str

    # Buton Renkleri
    button_primary_color: str
    button_border_color: str
    button_icon_color: str

    # Diğer
    avatar_url: Optional[str] = None
    animation_style: str
    language: str
    status: str
    script_token: str

    # İlişkiler (opsiyonel, detay endpoint'i için)
    stores: Optional[List[StoreBasicInfo]] = None
    products: Optional[List[ProductBasicInfo]] = None

    # İstatistikler
    store_count: int = 0
    product_count: int = 0
    conversation_count: int = 0
    knowledge_source_count: int = 0

    # Integration ayarları (store/product chatbox endpoint'leri için)
    show_on_homepage: Optional[bool] = None
    show_on_products: Optional[bool] = None
    show_on_product_page: Optional[bool] = None
    position: Optional[str] = None

    # Tarihler
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatboxStoreRelationCreate(BaseModel):
    """Create chatbox-store relation"""
    store_id: UUID
    show_on_homepage: bool = True
    show_on_products: bool = True
    position: str = Field("bottom-right", pattern=r'^(bottom-right|bottom-left|top-right|top-left)$')
    is_active: bool = True


class ChatboxStoreRelationUpdate(BaseModel):
    """Update chatbox-store relation"""
    show_on_homepage: Optional[bool] = None
    show_on_products: Optional[bool] = None
    position: Optional[str] = Field(None, pattern=r'^(bottom-right|bottom-left|top-right|top-left)$')
    is_active: Optional[bool] = None


class ChatboxStoreRelation(BaseModel):
    """Chatbox-Store relation response"""
    id: UUID
    store: StoreBasicInfo
    show_on_homepage: bool
    show_on_products: bool
    position: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatboxProductRelationCreate(BaseModel):
    """Create chatbox-product relation"""
    product_id: UUID
    show_on_product_page: bool = True
    show_on_store_homepage: bool = True
    is_active: bool = True


class ChatboxProductRelationUpdate(BaseModel):
    """Update chatbox-product relation"""
    show_on_product_page: Optional[bool] = None
    show_on_store_homepage: Optional[bool] = None
    is_active: Optional[bool] = None


class ChatboxProductRelation(BaseModel):
    """Chatbox-Product relation response"""
    id: UUID
    product: ProductBasicInfo
    show_on_product_page: bool
    show_on_store_homepage: bool = False  # Default value for backward compatibility
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatboxStoreBulkCreate(BaseModel):
    """Bulk create chatbox-store relations"""
    store_ids: List[UUID]
    settings: ChatboxStoreRelationCreate


class ChatboxStoreBulkResponse(BaseModel):
    """Response for bulk operations"""
    success_count: int
    failed_count: int
    skipped_count: int = 0
    results: List[Dict[str, Any]]


class ChatboxIntegrationsUpdate(BaseModel):
    """Update chatbox integrations (stores and products together)"""
    stores: List[ChatboxStoreRelationCreate] = Field(default_factory=list, description="Store integrations")
    products: List[ChatboxProductRelationCreate] = Field(default_factory=list, description="Product integrations")
    stores_only: List[UUID] = Field(default_factory=list, description="Store IDs marked as 'stores only'")


class ChatboxIntegrationsResponse(BaseModel):
    """Response for integration update"""
    stores_added: int
    products_added: int
    stores_removed: int
    products_removed: int
    message: str


class KnowledgeSourceResponse(BaseModel):
    """Knowledge source (PDF) response"""
    id: UUID
    chatbot_id: UUID
    source_type: str
    source_name: str
    storage_path: str
    file_size: Optional[int] = None
    status: str
    token_count: int
    error_message: Optional[str] = None
    is_active: bool = True
    content: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeSourceContentUpdate(BaseModel):
    """Update knowledge source content"""
    content: str = Field(..., min_length=1, description="Updated PDF content")


class KnowledgeSourceStatusResponse(BaseModel):
    """Knowledge source processing status"""
    id: UUID
    status: str
    progress: int = 0
    error_message: Optional[str] = None
    token_count: int
    processed_at: Optional[datetime] = None


class CreateEditedPDFRequest(BaseModel):
    """Request to create edited PDF from modified content"""
    original_source_id: UUID = Field(..., description="ID of the original PDF source")
    edited_content: str = Field(..., min_length=1, description="Edited PDF content")


class ChatboxStats(BaseModel):
    """Chatbox statistics"""
    total_conversations: int
    total_messages: int
    avg_latency_ms: float
    avg_rating: Optional[float] = None
    total_feedback: int

    store_count: int
    product_count: int
    knowledge_source_count: int
    total_tokens: int

    sentiment_distribution: Dict[str, int] = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }

    daily_conversations: List[Dict[str, Any]] = []
