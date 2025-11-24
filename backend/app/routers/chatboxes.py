from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, BackgroundTasks
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import secrets
import io
import time
from pypdf import PdfReader

from ..schemas.chatbox import (
    ChatboxResponse, ChatboxCreate, ChatboxUpdate, ChatboxList,
    ChatboxStoreRelation, ChatboxStoreRelationCreate, ChatboxStoreRelationUpdate,
    ChatboxProductRelation, ChatboxProductRelationCreate, ChatboxProductRelationUpdate,
    ChatboxStoreBulkCreate, ChatboxStoreBulkResponse,
    ChatboxIntegrationsUpdate, ChatboxIntegrationsResponse,
    KnowledgeSourceResponse, KnowledgeSourceContentUpdate, KnowledgeSourceStatusResponse,
    CreateEditedPDFRequest,
    ChatboxStats
)
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..schemas.knowledge import (
    ProcessChunksRequest, ProcessChunksResponse, ChunkResponse,
    ChunkListItem, ChunkStatistics
)
from ..dependencies import get_current_user, get_supabase_client
from ..services.chunking_service import chunking_service
from ..services.chunk_enrichment_service import chunk_enrichment_service

router = APIRouter(
    prefix="/chatboxes",
    tags=["Chatboxes"],
    responses={404: {"description": "Not found"}}
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text content from PDF bytes

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        Extracted text content
    """
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)

        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)

        return "\n\n".join(text_content)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for storage: remove Turkish characters and special chars

    Args:
        filename: Original filename with potentially Turkish characters

    Returns:
        Sanitized filename safe for storage
    """
    # Turkish character mapping
    char_map = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U',
        ' ': '_',
    }

    sanitized = filename
    for turkish_char, replacement in char_map.items():
        sanitized = sanitized.replace(turkish_char, replacement)

    # Remove any other non-ASCII characters
    sanitized = ''.join(char if ord(char) < 128 else '_' for char in sanitized)

    return sanitized


def create_pdf_from_text(text: str, filename: str) -> bytes:
    """
    Create a PDF file from text content using reportlab
    WITH TURKISH CHARACTER SUPPORT

    Args:
        text: Text content to convert to PDF (UTF-8)
        filename: Name for the PDF file (for metadata)

    Returns:
        PDF file content as bytes
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        # Register Turkish-compatible font (DejaVu Sans)
        font_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'fonts',
            'dejavu-fonts-ttf-2.37',
            'ttf',
            'DejaVuSans.ttf'
        )

        # Register font only once (check cache)
        if 'DejaVuSans' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            print(f"✅ [create_pdf_from_text] DejaVu Sans font registered")

        # Create PDF in memory
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=filename
        )

        # Container for PDF elements
        story = []

        # Get styles
        styles = getSampleStyleSheet()

        # Custom style for Turkish characters
        normal_style = ParagraphStyle(
            'TurkishNormal',
            parent=styles['Normal'],
            fontName='DejaVuSans',  # Use Turkish-compatible font
            fontSize=10,
            leading=14,
            wordWrap='CJK'  # Better word wrapping for non-Latin characters
        )

        # Split text into paragraphs
        paragraphs = text.split('\n')

        for para_text in paragraphs:
            if para_text.strip():
                # Escape XML special characters (but preserve UTF-8)
                safe_text = para_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                para = Paragraph(safe_text, normal_style)
                story.append(para)
                story.append(Spacer(1, 0.2*cm))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        buffer.seek(0)
        pdf_bytes = buffer.read()

        print(f"✅ [create_pdf_from_text] PDF created with Turkish character support ({len(pdf_bytes)} bytes)")
        return pdf_bytes

    except Exception as e:
        raise ValueError(f"Failed to create PDF from text: {str(e)}")


async def verify_chatbox_ownership(chatbox_id: str, current_user: dict, supabase) -> dict:
    """
    Helper function to verify chatbox ownership through user_id, brand, or store
    Returns chatbox data if owned, raises HTTPException otherwise
    """
    # Get chatbox first
    result = supabase.table("chatbots").select("*").eq("id", chatbox_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbox not found"
        )

    chatbox_data = result.data[0]

    # Verify ownership (through user_id, brand, or store)
    is_owned = False

    # Check direct user ownership (öncelik)
    if chatbox_data.get('user_id') == current_user["id"]:
        is_owned = True

    # Check brand ownership
    if not is_owned and chatbox_data.get('brand_id'):
        brand_check = supabase.table("brands").select("id").eq(
            "id", chatbox_data['brand_id']
        ).eq("user_id", current_user["id"]).execute()
        if brand_check.data:
            is_owned = True

    # Check store ownership
    if not is_owned and chatbox_data.get('store_id'):
        store_check = supabase.table("stores").select(
            "id, brands!inner(user_id)"
        ).eq("id", chatbox_data['store_id']).eq(
            "brands.user_id", current_user["id"]
        ).execute()
        if store_check.data:
            is_owned = True

    if not is_owned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbox not found or you don't have permission"
        )

    return chatbox_data


# ============================================================================
# PHASE 1: BASIC CRUD OPERATIONS
# ============================================================================

@router.post("/", response_model=ChatboxResponse, status_code=status.HTTP_201_CREATED)
async def create_chatbox(
    chatbox: ChatboxCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new chatbox

    - Only requires name, title, initial_message and 8 color fields
    - Brand_id and store_id are completely optional
    - Automatically sets user_id to current user
    - Generates unique script_token
    """
    try:
        # Generate unique script token
        script_token = secrets.token_urlsafe(32)

        # Prepare chatbox data
        chatbox_data = chatbox.model_dump(exclude_none=True)
        if chatbox.brand_id:
            chatbox_data["brand_id"] = str(chatbox.brand_id)
        if chatbox.store_id:
            chatbox_data["store_id"] = str(chatbox.store_id)
        chatbox_data["script_token"] = script_token
        chatbox_data["user_id"] = current_user["id"]  # Her chatbox kullanıcıya bağlı

        # Create chatbox
        result = supabase.table("chatbots").insert(chatbox_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create chatbox"
            )

        created_chatbox = result.data[0]

        return ChatboxResponse(**created_chatbox)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chatbox: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[ChatboxList])
async def list_chatboxes(
    brand_id: Optional[UUID] = None,
    store_id: Optional[UUID] = None,
    status_filter: Optional[str] = Query(None, pattern="^(draft|active|inactive)$"),
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of user's chatboxes with pagination and filters

    - Filters by brand_id if provided
    - Filters by store_id if provided
    - Filters by status if provided
    - Includes counts for stores, products, conversations, knowledge sources
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size

        # Build query - başlangıç olarak user_id ile filtrele
        all_chatboxes_query = supabase.table("chatbots").select(
            "*",
            count="exact"
        ).eq("user_id", current_user["id"])

        # Apply additional filters
        if brand_id:
            all_chatboxes_query = all_chatboxes_query.eq("brand_id", str(brand_id))
        if store_id:
            all_chatboxes_query = all_chatboxes_query.eq("store_id", str(store_id))
        if status_filter:
            all_chatboxes_query = all_chatboxes_query.eq("status", status_filter)

        # Get all chatboxes for user
        all_result = all_chatboxes_query.execute()

        # Kullanıcının chatbox'ları
        user_chatboxes = all_result.data if all_result.data else []

        total = len(user_chatboxes)

        # Apply pagination to filtered results
        paginated_chatboxes = user_chatboxes[offset:offset + pagination.size]

        # Get counts for each chatbox
        chatboxes_data = []
        for chatbox in paginated_chatboxes:
            chatbox_id = chatbox["id"]

            # Get store count
            store_count_result = supabase.table("chatbox_stores").select(
                "id", count="exact"
            ).eq("chatbox_id", chatbox_id).execute()
            store_count = store_count_result.count if store_count_result.count else 0

            # Get product count
            product_count_result = supabase.table("chatbox_products").select(
                "id", count="exact"
            ).eq("chatbox_id", chatbox_id).execute()
            product_count = product_count_result.count if product_count_result.count else 0

            # Get conversation count
            conversation_count_result = supabase.table("conversations").select(
                "id", count="exact"
            ).eq("chatbot_id", chatbox_id).execute()
            conversation_count = conversation_count_result.count if conversation_count_result.count else 0

            # Get knowledge source count
            knowledge_count_result = supabase.table("knowledge_base_entries").select(
                "id", count="exact"
            ).eq("chatbot_id", chatbox_id).execute()
            knowledge_count = knowledge_count_result.count if knowledge_count_result.count else 0

            chatbox_copy = chatbox.copy()
            chatbox_copy.pop('brands', None)
            chatbox_copy['store_count'] = store_count
            chatbox_copy['product_count'] = product_count
            chatbox_copy['conversation_count'] = conversation_count
            chatbox_copy['knowledge_source_count'] = knowledge_count

            chatboxes_data.append(ChatboxList(**chatbox_copy))

        return PaginationResponse(
            items=chatboxes_data,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatboxes: {str(e)}"
        )


@router.get("/{chatbox_id}", response_model=ChatboxResponse)
async def get_chatbox(
    chatbox_id: UUID,
    include_relations: bool = Query(False, description="Include stores and products"),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific chatbox by ID

    - Validates ownership
    - Optionally includes related stores and products
    - Includes all statistics
    """
    try:
        # Verify ownership
        chatbox_data = await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)
        chatbox_data = chatbox_data.copy()

        # Get counts
        chatbox_id_str = str(chatbox_id)

        store_count_result = supabase.table("chatbox_stores").select(
            "id", count="exact"
        ).eq("chatbox_id", chatbox_id_str).execute()
        chatbox_data['store_count'] = store_count_result.count if store_count_result.count else 0

        product_count_result = supabase.table("chatbox_products").select(
            "id", count="exact"
        ).eq("chatbox_id", chatbox_id_str).execute()
        chatbox_data['product_count'] = product_count_result.count if product_count_result.count else 0

        conversation_count_result = supabase.table("conversations").select(
            "id", count="exact"
        ).eq("chatbot_id", chatbox_id_str).execute()
        chatbox_data['conversation_count'] = conversation_count_result.count if conversation_count_result.count else 0

        knowledge_count_result = supabase.table("knowledge_base_entries").select(
            "id", count="exact"
        ).eq("chatbot_id", chatbox_id_str).execute()
        chatbox_data['knowledge_source_count'] = knowledge_count_result.count if knowledge_count_result.count else 0

        # Get relations if requested
        if include_relations:
            # Get stores
            stores_result = supabase.table("chatbox_stores").select(
                "stores(id, name, slug, logo)"
            ).eq("chatbox_id", chatbox_id_str).execute()

            if stores_result.data:
                chatbox_data['stores'] = [
                    item['stores'] for item in stores_result.data if item.get('stores')
                ]

            # Get products
            products_result = supabase.table("chatbox_products").select(
                "products(id, name, slug, price, category, store:stores(name))"
            ).eq("chatbox_id", chatbox_id_str).execute()

            if products_result.data:
                products = []
                for item in products_result.data:
                    if item.get('products'):
                        product = item['products'].copy()
                        if product.get('store'):
                            product['store_name'] = product['store']['name']
                            product.pop('store', None)
                        products.append(product)
                chatbox_data['products'] = products

        return ChatboxResponse(**chatbox_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbox: {str(e)}"
        )


@router.put("/{chatbox_id}", response_model=ChatboxResponse)
async def update_chatbox(
    chatbox_id: UUID,
    chatbox_update: ChatboxUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific chatbox

    - All fields are optional
    - Validates ownership
    - Cannot update script_token
    - Can update brand_id or store_id
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Prepare update data
        update_data = chatbox_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update chatbox
        result = supabase.table("chatbots").update(update_data).eq(
            "id", str(chatbox_id)
        ).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update chatbox"
            )

        updated_data = result.data[0]

        # Get counts
        chatbox_id_str = str(chatbox_id)

        store_count_result = supabase.table("chatbox_stores").select(
            "id", count="exact"
        ).eq("chatbox_id", chatbox_id_str).execute()
        updated_data['store_count'] = store_count_result.count if store_count_result.count else 0

        product_count_result = supabase.table("chatbox_products").select(
            "id", count="exact"
        ).eq("chatbox_id", chatbox_id_str).execute()
        updated_data['product_count'] = product_count_result.count if product_count_result.count else 0

        conversation_count_result = supabase.table("conversations").select(
            "id", count="exact"
        ).eq("chatbot_id", chatbox_id_str).execute()
        updated_data['conversation_count'] = conversation_count_result.count if conversation_count_result.count else 0

        knowledge_count_result = supabase.table("knowledge_base_entries").select(
            "id", count="exact"
        ).eq("chatbot_id", chatbox_id_str).execute()
        updated_data['knowledge_source_count'] = knowledge_count_result.count if knowledge_count_result.count else 0

        return ChatboxResponse(**updated_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chatbox: {str(e)}"
        )


@router.delete("/{chatbox_id}", response_model=StatusResponse)
async def delete_chatbox(
    chatbox_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific chatbox

    - Validates ownership
    - CASCADE deletes all relations (stores, products, knowledge sources, conversations)
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Delete chatbox (CASCADE will delete related records)
        result = supabase.table("chatbots").delete().eq("id", str(chatbox_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete chatbox"
            )

        return StatusResponse(
            success=True,
            message="Chatbox deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chatbox: {str(e)}"
        )


# ============================================================================
# PHASE 2: STORE RELATIONS
# ============================================================================

@router.get("/{chatbox_id}/stores", response_model=List[ChatboxStoreRelation])
async def get_chatbox_stores(
    chatbox_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get all stores associated with a chatbox
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get store relations
        result = supabase.table("chatbox_stores").select(
            "id, show_on_homepage, show_on_products, position, is_active, created_at, stores(id, name, slug, logo)"
        ).eq("chatbox_id", str(chatbox_id)).execute()

        relations = []
        for item in result.data if result.data else []:
            if item.get('stores'):
                relation_data = {
                    'id': item['id'],
                    'store': item['stores'],
                    'show_on_homepage': item['show_on_homepage'],
                    'show_on_products': item['show_on_products'],
                    'position': item['position'],
                    'is_active': item['is_active'],
                    'created_at': item['created_at']
                }
                relations.append(ChatboxStoreRelation(**relation_data))

        return relations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get store relations: {str(e)}"
        )


@router.post("/{chatbox_id}/stores", response_model=ChatboxStoreRelation, status_code=status.HTTP_201_CREATED)
async def add_store_to_chatbox(
    chatbox_id: UUID,
    relation: ChatboxStoreRelationCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Add a store to a chatbox

    - Validates chatbox and store ownership
    - Prevents duplicate relations
    """
    try:
        # Verify ownership
        chatbox_data = await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)
        brand_id = chatbox_data.get('brand_id')

        # Verify store belongs to same brand
        store_check = supabase.table("stores").select("id").eq(
            "id", str(relation.store_id)
        ).eq("brand_id", brand_id).execute()

        if not store_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or doesn't belong to the same brand"
            )

        # Check if relation already exists
        existing_check = supabase.table("chatbox_stores").select("id").eq(
            "chatbox_id", str(chatbox_id)
        ).eq("store_id", str(relation.store_id)).execute()

        if existing_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store is already added to this chatbox"
            )

        # Create relation
        relation_data = relation.model_dump()
        relation_data["chatbox_id"] = str(chatbox_id)
        relation_data["store_id"] = str(relation.store_id)

        result = supabase.table("chatbox_stores").insert(relation_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add store to chatbox"
            )

        # Get created relation with store data
        relation_id = result.data[0]['id']
        created_result = supabase.table("chatbox_stores").select(
            "id, show_on_homepage, show_on_products, position, is_active, created_at, stores(id, name, slug, logo)"
        ).eq("id", relation_id).execute()

        if not created_result.data or not created_result.data[0].get('stores'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created relation"
            )

        item = created_result.data[0]
        relation_response = {
            'id': item['id'],
            'store': item['stores'],
            'show_on_homepage': item['show_on_homepage'],
            'show_on_products': item['show_on_products'],
            'position': item['position'],
            'is_active': item['is_active'],
            'created_at': item['created_at']
        }

        return ChatboxStoreRelation(**relation_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add store to chatbox: {str(e)}"
        )


@router.put("/{chatbox_id}/stores/{store_id}", response_model=ChatboxStoreRelation)
async def update_chatbox_store_relation(
    chatbox_id: UUID,
    store_id: UUID,
    relation_update: ChatboxStoreRelationUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update store-chatbox relation settings
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Check if relation exists
        relation_check = supabase.table("chatbox_stores").select("id").eq(
            "chatbox_id", str(chatbox_id)
        ).eq("store_id", str(store_id)).execute()

        if not relation_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store relation not found"
            )

        relation_id = relation_check.data[0]['id']

        # Prepare update data
        update_data = relation_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update relation
        supabase.table("chatbox_stores").update(update_data).eq("id", relation_id).execute()

        # Get updated relation
        updated_result = supabase.table("chatbox_stores").select(
            "id, show_on_homepage, show_on_products, position, is_active, created_at, stores(id, name, slug, logo)"
        ).eq("id", relation_id).execute()

        if not updated_result.data or not updated_result.data[0].get('stores'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated relation"
            )

        item = updated_result.data[0]
        relation_response = {
            'id': item['id'],
            'store': item['stores'],
            'show_on_homepage': item['show_on_homepage'],
            'show_on_products': item['show_on_products'],
            'position': item['position'],
            'is_active': item['is_active'],
            'created_at': item['created_at']
        }

        return ChatboxStoreRelation(**relation_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update store relation: {str(e)}"
        )


@router.delete("/{chatbox_id}/stores/{store_id}", response_model=StatusResponse)
async def remove_store_from_chatbox(
    chatbox_id: UUID,
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Remove a store from a chatbox
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Delete relation
        result = supabase.table("chatbox_stores").delete().eq(
            "chatbox_id", str(chatbox_id)
        ).eq("store_id", str(store_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store relation not found"
            )

        return StatusResponse(
            success=True,
            message="Store removed from chatbox successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove store from chatbox: {str(e)}"
        )


@router.post("/{chatbox_id}/stores/bulk", response_model=ChatboxStoreBulkResponse)
async def bulk_add_stores_to_chatbox(
    chatbox_id: UUID,
    bulk_create: ChatboxStoreBulkCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Add multiple stores to a chatbox at once

    - Validates all stores belong to the same brand
    - Skips stores that are already added
    - Returns detailed results for each store
    """
    try:
        # Verify ownership
        chatbox_data = await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)
        brand_id = chatbox_data.get('brand_id')

        # Get existing relations
        existing_result = supabase.table("chatbox_stores").select("store_id").eq(
            "chatbox_id", str(chatbox_id)
        ).execute()

        existing_store_ids = {item['store_id'] for item in existing_result.data} if existing_result.data else set()

        success_count = 0
        failed_count = 0
        skipped_count = 0
        results = []

        for store_id in bulk_create.store_ids:
            store_id_str = str(store_id)

            # Check if already exists
            if store_id_str in existing_store_ids:
                skipped_count += 1
                results.append({
                    "store_id": store_id_str,
                    "success": False,
                    "message": "Already added",
                    "skipped": True
                })
                continue

            # Verify store belongs to brand
            store_check = supabase.table("stores").select("id").eq(
                "id", store_id_str
            ).eq("brand_id", brand_id).execute()

            if not store_check.data:
                failed_count += 1
                results.append({
                    "store_id": store_id_str,
                    "success": False,
                    "message": "Store not found or doesn't belong to the same brand"
                })
                continue

            # Create relation
            try:
                relation_data = bulk_create.settings.model_dump()
                relation_data["chatbox_id"] = str(chatbox_id)
                relation_data["store_id"] = store_id_str

                insert_result = supabase.table("chatbox_stores").insert(relation_data).execute()

                if insert_result.data:
                    success_count += 1
                    results.append({
                        "store_id": store_id_str,
                        "success": True,
                        "message": "Added successfully",
                        "relation_id": insert_result.data[0]['id']
                    })
                else:
                    failed_count += 1
                    results.append({
                        "store_id": store_id_str,
                        "success": False,
                        "message": "Failed to create relation"
                    })
            except Exception as e:
                failed_count += 1
                results.append({
                    "store_id": store_id_str,
                    "success": False,
                    "message": str(e)
                })

        return ChatboxStoreBulkResponse(
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk add stores: {str(e)}"
        )


# ============================================================================
# PHASE 3: PRODUCT RELATIONS
# ============================================================================

@router.get("/{chatbox_id}/products", response_model=List[ChatboxProductRelation])
async def get_chatbox_products(
    chatbox_id: UUID,
    store_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get all products associated with a chatbox

    - Optionally filter by store_id
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get product relations
        query = supabase.table("chatbox_products").select(
            "id, show_on_product_page, is_active, created_at, products(id, name, slug, price, category, store:stores(name))"
        ).eq("chatbox_id", str(chatbox_id))

        # Filter by store if provided
        if store_id:
            query = query.eq("products.store_id", str(store_id))

        result = query.execute()

        relations = []
        for item in result.data if result.data else []:
            if item.get('products'):
                product_data = item['products'].copy()
                if product_data.get('store'):
                    product_data['store_name'] = product_data['store']['name']
                    product_data.pop('store', None)
                
                # price değerini string'e çevir (ProductBasicInfo şeması str bekliyor)
                if 'price' in product_data and product_data['price'] is not None:
                    product_data['price'] = str(product_data['price'])

                relation_data = {
                    'id': item['id'],
                    'product': product_data,
                    'show_on_product_page': item['show_on_product_page'],
                    'is_active': item['is_active'],
                    'created_at': item['created_at']
                }
                relations.append(ChatboxProductRelation(**relation_data))

        return relations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product relations: {str(e)}"
        )


@router.post("/{chatbox_id}/products", response_model=ChatboxProductRelation, status_code=status.HTTP_201_CREATED)
async def add_product_to_chatbox(
    chatbox_id: UUID,
    relation: ChatboxProductRelationCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Add a product to a chatbox

    - Validates chatbox and product ownership
    - Prevents duplicate relations
    """
    try:
        # Verify ownership
        chatbox_data = await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)
        brand_id = chatbox_data.get('brand_id')

        # Verify product belongs to a store in the same brand
        product_check = supabase.table("products").select(
            "id, stores!inner(brand_id)"
        ).eq("id", str(relation.product_id)).eq("stores.brand_id", brand_id).execute()

        if not product_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or doesn't belong to the same brand"
            )

        # Check if product is already used in ANY chatbox (global check)
        global_check = supabase.table("chatbox_products").select(
            "chatbox_id, chatbots!inner(name)"
        ).eq("product_id", str(relation.product_id)).execute()

        if global_check.data:
            existing_chatbox_name = global_check.data[0]['chatbots']['name']
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu ürün zaten '{existing_chatbox_name}' chatbox'ında kullanılıyor"
            )

        # Create relation
        relation_data = relation.model_dump()
        relation_data["chatbox_id"] = str(chatbox_id)
        relation_data["product_id"] = str(relation.product_id)

        result = supabase.table("chatbox_products").insert(relation_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add product to chatbox"
            )

        # Get created relation with product data
        relation_id = result.data[0]['id']
        created_result = supabase.table("chatbox_products").select(
            "id, show_on_product_page, is_active, created_at, products(id, name, slug, price, category, store:stores(name))"
        ).eq("id", relation_id).execute()

        if not created_result.data or not created_result.data[0].get('products'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created relation"
            )

        item = created_result.data[0]
        product_data = item['products'].copy()
        if product_data.get('store'):
            product_data['store_name'] = product_data['store']['name']
            product_data.pop('store', None)
        
        # price değerini string'e çevir (ProductBasicInfo şeması str bekliyor)
        if 'price' in product_data and product_data['price'] is not None:
            product_data['price'] = str(product_data['price'])

        relation_response = {
            'id': item['id'],
            'product': product_data,
            'show_on_product_page': item['show_on_product_page'],
            'is_active': item['is_active'],
            'created_at': item['created_at']
        }

        return ChatboxProductRelation(**relation_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add product to chatbox: {str(e)}"
        )


@router.put("/{chatbox_id}/products/{product_id}", response_model=ChatboxProductRelation)
async def update_chatbox_product_relation(
    chatbox_id: UUID,
    product_id: UUID,
    relation_update: ChatboxProductRelationUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update product-chatbox relation settings
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Check if relation exists
        relation_check = supabase.table("chatbox_products").select("id").eq(
            "chatbox_id", str(chatbox_id)
        ).eq("product_id", str(product_id)).execute()

        if not relation_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product relation not found"
            )

        relation_id = relation_check.data[0]['id']

        # Prepare update data
        update_data = relation_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update relation
        supabase.table("chatbox_products").update(update_data).eq("id", relation_id).execute()

        # Get updated relation
        updated_result = supabase.table("chatbox_products").select(
            "id, show_on_product_page, is_active, created_at, products(id, name, slug, price, category, store:stores(name))"
        ).eq("id", relation_id).execute()

        if not updated_result.data or not updated_result.data[0].get('products'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated relation"
            )

        item = updated_result.data[0]
        product_data = item['products'].copy()
        if product_data.get('store'):
            product_data['store_name'] = product_data['store']['name']
            product_data.pop('store', None)
        
        # price değerini string'e çevir (ProductBasicInfo şeması str bekliyor)
        if 'price' in product_data and product_data['price'] is not None:
            product_data['price'] = str(product_data['price'])

        relation_response = {
            'id': item['id'],
            'product': product_data,
            'show_on_product_page': item['show_on_product_page'],
            'is_active': item['is_active'],
            'created_at': item['created_at']
        }

        return ChatboxProductRelation(**relation_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product relation: {str(e)}"
        )


@router.delete("/{chatbox_id}/products/{product_id}", response_model=StatusResponse)
async def remove_product_from_chatbox(
    chatbox_id: UUID,
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Remove a product from a chatbox
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Delete relation
        result = supabase.table("chatbox_products").delete().eq(
            "chatbox_id", str(chatbox_id)
        ).eq("product_id", str(product_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product relation not found"
            )

        return StatusResponse(
            success=True,
            message="Product removed from chatbox successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove product from chatbox: {str(e)}"
        )


@router.post("/{chatbox_id}/products/bulk/store/{store_id}", response_model=ChatboxStoreBulkResponse)
async def bulk_add_store_products_to_chatbox(
    chatbox_id: UUID,
    store_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Add all products from a store to a chatbox

    - Validates store belongs to same brand
    - Skips products that are already added
    """
    try:
        # Verify ownership
        chatbox_data = await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)
        brand_id = chatbox_data.get('brand_id')

        # Verify store belongs to brand
        store_check = supabase.table("stores").select("id").eq(
            "id", str(store_id)
        ).eq("brand_id", brand_id).execute()

        if not store_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or doesn't belong to the same brand"
            )

        # Get all products from store
        products_result = supabase.table("products").select("id").eq(
            "store_id", str(store_id)
        ).execute()

        if not products_result.data:
            return ChatboxStoreBulkResponse(
                success_count=0,
                failed_count=0,
                skipped_count=0,
                results=[],
                message="No products found in this store"
            )

        # Get ALL existing product relations (global check)
        all_existing_result = supabase.table("chatbox_products").select(
            "product_id, chatbox_id, chatbots!inner(name)"
        ).execute()

        # Create a map of product_id -> chatbox_name for products already in use
        product_chatbox_map = {}
        if all_existing_result.data:
            for item in all_existing_result.data:
                product_chatbox_map[item['product_id']] = item['chatbots']['name']

        success_count = 0
        failed_count = 0
        skipped_count = 0
        results = []

        for product in products_result.data:
            product_id = product['id']

            # Check if product is already used in ANY chatbox
            if product_id in product_chatbox_map:
                existing_chatbox = product_chatbox_map[product_id]
                skipped_count += 1
                results.append({
                    "product_id": product_id,
                    "success": False,
                    "message": f"Ürün zaten '{existing_chatbox}' chatbox'ında kullanılıyor",
                    "skipped": True
                })
                continue

            # Create relation
            try:
                relation_data = {
                    "chatbox_id": str(chatbox_id),
                    "product_id": product_id,
                    "show_on_product_page": True,
                    "is_active": True
                }

                insert_result = supabase.table("chatbox_products").insert(relation_data).execute()

                if insert_result.data:
                    success_count += 1
                    results.append({
                        "product_id": product_id,
                        "success": True,
                        "message": "Added successfully",
                        "relation_id": insert_result.data[0]['id']
                    })
                else:
                    failed_count += 1
                    results.append({
                        "product_id": product_id,
                        "success": False,
                        "message": "Failed to create relation"
                    })
            except Exception as e:
                failed_count += 1
                results.append({
                    "product_id": product_id,
                    "success": False,
                    "message": str(e)
                })

        return ChatboxStoreBulkResponse(
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk add products: {str(e)}"
        )


# ============================================================================
# PHASE 4: KNOWLEDGE SOURCES (PDF)
# ============================================================================

@router.post("/temp-knowledge-sources", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_temp_knowledge_source(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Upload a temporary PDF knowledge source (without chatbox assignment)

    - Used during chatbox creation flow
    - PDF will be assigned to chatbox later
    - chatbot_id will be NULL initially
    """
    try:
        # Validate file type
        if not file.content_type or 'pdf' not in file.content_type.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Generate unique file name
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
        unique_filename = f"temp_{uuid4()}.{file_extension}"
        storage_path = f"temp/{current_user['id']}/{unique_filename}"

        # Upload to Supabase Storage
        upload_result = supabase.storage.from_("chatbox-knowledge").upload(
            storage_path,
            file_content,
            {
                "content-type": file.content_type,
                "upsert": "false"
            }
        )

        # Extract text from PDF
        try:
            extracted_text = extract_text_from_pdf(file_content)
            pdf_status = "processed"
        except Exception as e:
            extracted_text = None
            pdf_status = "failed"
            print(f"❌ PDF metin çıkarma hatası: {str(e)}")

        # Create database record WITHOUT chatbot_id
        knowledge_data = {
            "chatbot_id": None,  # NULL - will be assigned later
            "source_type": "pdf",
            "source_name": file.filename,
            "storage_path": storage_path,
            "file_size": file_size,
            "content": extracted_text,
            "status": pdf_status,
            "token_count": len(extracted_text) // 4 if extracted_text else 0,
            "is_active": True
        }

        result = supabase.table("knowledge_base_entries").insert(knowledge_data).execute()

        if not result.data:
            # Clean up uploaded file if database insert fails
            try:
                supabase.storage.from_("chatbox-knowledge").remove([storage_path])
            except:
                pass

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create knowledge source record"
            )

        source_id = result.data[0]["id"]

        # Automatically process chunks after upload
        chunks_created = 0
        try:
            # Chunk the extracted text
            chunks = chunking_service.chunk_text(
                text=extracted_text if extracted_text else "",
                source_name=file.filename
            )

            if chunks:
                # Prepare chunk records
                chunk_records = []
                for chunk in chunks:
                    chunk_records.append({
                        "knowledge_entry_id": source_id,
                        "chatbot_id": None,  # NULL - will be assigned later
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "token_count": chunk["token_count"],
                        "metadata": chunk["metadata"]
                    })

                # Insert chunks
                chunks_insert = supabase.table("knowledge_chunks").insert(chunk_records).execute()
                chunks_created = len(chunks_insert.data) if chunks_insert.data else 0

                print(f"✅ Created {chunks_created} chunks for temp knowledge source {source_id}")

                # Start AI enrichment for temp PDF (without chatbox_id)
                if chunks_created > 0:
                    try:
                        enrichment_job = await chunk_enrichment_service.create_enrichment_job(
                            knowledge_entry_id=source_id,
                            chatbot_id=None,  # NULL initially
                            user_id=current_user["id"],
                            prompt_template=None,
                            ai_model=None
                        )

                        background_tasks.add_task(
                            chunk_enrichment_service.enrich_all_chunks_background,
                            job_id=enrichment_job['id'],
                            knowledge_entry_id=source_id,
                            prompt_template=None,
                            ai_model=None
                        )

                        print(f"✅ Started AI enrichment job {enrichment_job['id']} for temp PDF")
                    except Exception as enrichment_error:
                        print(f"⚠️ Failed to start enrichment job: {str(enrichment_error)}")

        except Exception as chunk_error:
            print(f"⚠️ Failed to create chunks: {str(chunk_error)}")

        return KnowledgeSourceResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload temp knowledge source: {str(e)}"
        )


@router.post("/{chatbox_id}/knowledge-sources", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_source(
    chatbox_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Upload a PDF knowledge source to a chatbox

    - Validates file type (PDF only)
    - Uploads to Supabase Storage
    - Creates database record with processing status
    - TODO: Trigger vector embedding process
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Validate file type
        if not file.content_type or 'pdf' not in file.content_type.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Generate unique file name
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
        unique_filename = f"{uuid4()}.{file_extension}"
        storage_path = f"{chatbox_id}/{unique_filename}"

        # Upload to Supabase Storage
        upload_result = supabase.storage.from_("chatbox-knowledge").upload(
            storage_path,
            file_content,
            {
                "content-type": file.content_type,
                "upsert": "false"
            }
        )

        # Extract text from PDF
        try:
            extracted_text = extract_text_from_pdf(file_content)
            pdf_status = "processed"  # İşlem başarılı (DB'de allowed: pending, processing, ready, processed, failed)
        except Exception as e:
            extracted_text = None
            pdf_status = "failed"
            print(f"❌ PDF metin çıkarma hatası: {str(e)}")

        # Create database record
        knowledge_data = {
            "chatbot_id": str(chatbox_id),
            "source_type": "pdf",
            "source_name": file.filename,
            "storage_path": storage_path,
            "file_size": file_size,
            "content": extracted_text,  # PDF içeriğini kaydet
            "status": pdf_status,
            "token_count": len(extracted_text) // 4 if extracted_text else 0,  # Yaklaşık token sayısı
            "is_active": True  # Varsayılan olarak aktif
        }

        result = supabase.table("knowledge_base_entries").insert(knowledge_data).execute()

        if not result.data:
            # Clean up uploaded file if database insert fails
            try:
                supabase.storage.from_("chatbox-knowledge").remove([storage_path])
            except:
                pass

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create knowledge source record"
            )

        # Automatically process chunks after upload
        source_id = result.data[0]["id"]
        chunks_created = 0

        try:
            # Chunk the extracted text
            chunks = chunking_service.chunk_text(
                text=extracted_text if extracted_text else "",
                source_name=file.filename
            )

            if chunks:
                # Prepare chunk records
                chunk_records = []
                for chunk in chunks:
                    chunk_records.append({
                        "knowledge_entry_id": source_id,
                        "chatbot_id": str(chatbox_id),
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "token_count": chunk["token_count"],
                        "metadata": chunk["metadata"]
                    })

                # Insert chunks
                chunks_insert = supabase.table("knowledge_chunks").insert(chunk_records).execute()
                chunks_created = len(chunks_insert.data) if chunks_insert.data else 0

                print(f"✅ Created {chunks_created} chunks for knowledge source {source_id}")

                # Automatically start AI enrichment job after chunks are created
                if chunks_created > 0:
                    try:
                        enrichment_job = await chunk_enrichment_service.create_enrichment_job(
                            knowledge_entry_id=source_id,
                            chatbot_id=str(chatbox_id),
                            user_id=current_user["id"],
                            prompt_template=None,  # Use default prompt
                            ai_model=None  # Use default model
                        )

                        # Start background enrichment task with AI logging parameters
                        background_tasks.add_task(
                            chunk_enrichment_service.enrich_all_chunks_background,
                            job_id=enrichment_job['id'],
                            knowledge_entry_id=source_id,
                            prompt_template=None,
                            ai_model=None,
                            chatbot_id=str(chatbox_id),  # ✅ AI loglama için eklendi
                            user_id=current_user["id"]   # ✅ AI loglama için eklendi
                        )

                        print(f"✅ Started AI enrichment job {enrichment_job['id']} for {chunks_created} chunks")
                    except Exception as enrichment_error:
                        # Don't fail the upload if enrichment fails, just log it
                        print(f"⚠️ Failed to start enrichment job: {str(enrichment_error)}")
        except Exception as chunk_error:
            # Don't fail the upload if chunking fails, just log it
            print(f"⚠️ Failed to create chunks: {str(chunk_error)}")

        return KnowledgeSourceResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload knowledge source: {str(e)}"
        )


@router.get("/{chatbox_id}/knowledge-sources", response_model=List[KnowledgeSourceResponse])
async def list_knowledge_sources(
    chatbox_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get all knowledge sources for a chatbox
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get knowledge sources
        result = supabase.table("knowledge_base_entries").select("*").eq(
            "chatbot_id", str(chatbox_id)
        ).order("created_at", desc=True).execute()

        return [KnowledgeSourceResponse(**source) for source in result.data] if result.data else []

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge sources: {str(e)}"
        )


@router.get("/{chatbox_id}/knowledge-sources/{source_id}/status", response_model=KnowledgeSourceStatusResponse)
async def get_knowledge_source_status(
    chatbox_id: UUID,
    source_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get processing status of a knowledge source
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get knowledge source status
        result = supabase.table("knowledge_base_entries").select(
            "id, status, error_message, token_count, updated_at"
        ).eq("id", str(source_id)).eq("chatbot_id", str(chatbox_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )

        source_data = result.data[0]

        # Calculate progress (0-100)
        progress = 0
        if source_data['status'] == 'processing':
            progress = 50  # TODO: Implement actual progress tracking
        elif source_data['status'] == 'completed':
            progress = 100

        return KnowledgeSourceStatusResponse(
            id=source_data['id'],
            status=source_data['status'],
            progress=progress,
            error_message=source_data.get('error_message'),
            token_count=source_data['token_count'],
            processed_at=source_data.get('updated_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge source status: {str(e)}"
        )


@router.patch("/{chatbox_id}/knowledge-sources/{source_id}/content", response_model=KnowledgeSourceResponse)
async def update_knowledge_source_content(
    chatbox_id: UUID,
    source_id: UUID,
    body: KnowledgeSourceContentUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update knowledge source content (user edited)

    - Updates PDF content in database
    - Recalculates token count
    - Updates timestamp
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Check if source exists
        check_result = supabase.table("knowledge_base_entries").select("id").eq(
            "id", str(source_id)
        ).eq("chatbot_id", str(chatbox_id)).execute()

        if not check_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )

        # Calculate new token count (rough estimate: characters / 4)
        new_token_count = len(body.content) // 4 if body.content else 0

        # Update content
        update_result = supabase.table("knowledge_base_entries").update({
            "content": body.content,
            "token_count": new_token_count,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", str(source_id)).eq("chatbot_id", str(chatbox_id)).execute()

        if not update_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update knowledge source content"
            )

        return KnowledgeSourceResponse(**update_result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge source content: {str(e)}"
        )


@router.patch("/{chatbox_id}/knowledge-sources/{source_id}/toggle", response_model=KnowledgeSourceResponse)
async def toggle_knowledge_source_status(
    chatbox_id: UUID,
    source_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Toggle knowledge source active/inactive status

    - Switches between active and inactive
    - Returns updated knowledge source
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get current status
        result = supabase.table("knowledge_base_entries").select(
            "is_active"
        ).eq("id", str(source_id)).eq("chatbot_id", str(chatbox_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )

        current_status = result.data[0].get('is_active', True)
        new_status = not current_status

        # Update status
        update_result = supabase.table("knowledge_base_entries").update({
            "is_active": new_status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", str(source_id)).eq("chatbot_id", str(chatbox_id)).execute()

        if not update_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update knowledge source status"
            )

        return KnowledgeSourceResponse(**update_result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle knowledge source status: {str(e)}"
        )


@router.delete("/{chatbox_id}/knowledge-sources/{source_id}", response_model=StatusResponse)
async def delete_knowledge_source(
    chatbox_id: UUID,
    source_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a knowledge source

    - Deletes from storage
    - Deletes database record
    - TODO: Delete associated vector embeddings
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get knowledge source to get storage path
        source_result = supabase.table("knowledge_base_entries").select(
            "storage_path"
        ).eq("id", str(source_id)).eq("chatbot_id", str(chatbox_id)).execute()

        if not source_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )

        storage_path = source_result.data[0]['storage_path']

        # Delete from storage
        try:
            supabase.storage.from_("chatbox-knowledge").remove([storage_path])
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete file from storage: {str(e)}")

        # Delete from database
        result = supabase.table("knowledge_base_entries").delete().eq(
            "id", str(source_id)
        ).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete knowledge source"
            )

        # TODO: Delete associated vector embeddings from vector database

        return StatusResponse(
            success=True,
            message="Knowledge source deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete knowledge source: {str(e)}"
        )


@router.post("/{chatbox_id}/knowledge-sources/create-edited", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_edited_pdf(
    chatbox_id: UUID,
    request: CreateEditedPDFRequest,
    background_tasks: BackgroundTasks,  # ✅ Eklendi: Otomatik chunking ve enrichment için
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create edited PDF from modified content

    - Makes original PDF inactive
    - Creates new PDF record with edited content
    - New PDF name: [original_name]-Düzenlenmiş.pdf
    - New PDF is active by default
    - **Otomatik chunking ve AI enrichment** başlatır
    """
    try:
        # Verify chatbox ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        chatbox_id_str = str(chatbox_id)
        original_source_id_str = str(request.original_source_id)

        # Get original PDF source
        original_result = supabase.table("knowledge_base_entries").select("*").eq(
            "id", original_source_id_str
        ).eq("chatbot_id", chatbox_id_str).execute()

        if not original_result.data or len(original_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original PDF not found"
            )

        original_source = original_result.data[0]

        # Make original PDF inactive
        supabase.table("knowledge_base_entries").update({
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", original_source_id_str).execute()

        # Create new filename: [original_name]-Düzenlenmiş.pdf
        original_name = original_source.get("source_name", "document.pdf")
        if original_name.lower().endswith('.pdf'):
            name_without_ext = original_name[:-4]
            edited_name = f"{name_without_ext}-Düzenlenmiş.pdf"
        else:
            edited_name = f"{original_name}-Düzenlenmiş.pdf"

        # Create PDF from edited content
        try:
            pdf_bytes = create_pdf_from_text(request.edited_content, edited_name)
            pdf_size = len(pdf_bytes)
            print(f"📄 [create_edited_pdf] PDF oluşturuldu: {edited_name} ({pdf_size} bytes)")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF: {str(e)}"
            )

        # Upload to Supabase Storage
        new_pdf_id = uuid4()
        # Sanitize filename for storage (remove Turkish characters)
        safe_filename = sanitize_filename(edited_name)
        storage_path = f"{chatbox_id_str}/{new_pdf_id}_{safe_filename}"

        try:
            upload_result = supabase.storage.from_("chatbox-knowledge").upload(
                storage_path,
                pdf_bytes,
                {
                    "content-type": "application/pdf",
                    "upsert": "false"
                }
            )
            print(f"☁️  [create_edited_pdf] Storage'a yüklendi: {storage_path}")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload PDF to storage: {str(e)}"
            )

        # Create new PDF record with 'pending' status for auto-processing
        new_source_data = {
            "chatbot_id": chatbox_id_str,
            "source_type": "pdf",
            "source_name": edited_name,
            "content": request.edited_content,
            "token_count": len(request.edited_content) // 4,  # Approximate token count
            "status": "pending",  # ✅ Değişti: Otomatik işleme için 'pending' olarak başla
            "is_active": True,
            "storage_path": storage_path,  # New storage path
            "file_size": pdf_size,  # New file size
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        result = supabase.table("knowledge_base_entries").insert(new_source_data).execute()

        if not result.data:
            # Clean up uploaded file if database insert fails
            try:
                supabase.storage.from_("chatbox-knowledge").remove([storage_path])
            except:
                pass

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create edited PDF record"
            )

        created_entry = result.data[0]
        source_id = created_entry["id"]

        print(f"✅ [create_edited_pdf] Düzenlenmiş PDF oluşturuldu: {edited_name}")
        print(f"   - Orijinal PDF ({original_name}) pasif yapıldı")
        print(f"   - Yeni PDF aktif: {edited_name}")
        print(f"   - Storage path: {storage_path}")

        # 🚀 OTOMATIK İŞLEME: Chunking ve AI Enrichment başlat
        try:
            # Status'u processing yap
            supabase.table("knowledge_base_entries").update({
                "status": "processing"
            }).eq("id", source_id).execute()

            # Chunk'lara ayır
            chunks = chunking_service.chunk_text(
                text=request.edited_content,
                source_name=edited_name
            )

            if chunks:
                # Chunk kayıtları oluştur
                chunk_records = []
                for chunk in chunks:
                    chunk_records.append({
                        "knowledge_entry_id": source_id,
                        "chatbot_id": chatbox_id_str,
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "token_count": chunk["token_count"],
                        "metadata": chunk["metadata"]
                    })

                # Chunk'ları kaydet
                chunks_insert = supabase.table("knowledge_chunks").insert(chunk_records).execute()
                chunks_created = len(chunks_insert.data) if chunks_insert.data else 0

                print(f"✅ [create_edited_pdf] {chunks_created} chunk oluşturuldu")

                # AI enrichment job başlat
                if chunks_created > 0:
                    enrichment_job = await chunk_enrichment_service.create_enrichment_job(
                        knowledge_entry_id=source_id,
                        chatbot_id=chatbox_id_str,
                        user_id=current_user["id"],
                        prompt_template=None,
                        ai_model=None
                    )

                    # Background enrichment task (AI loglama ile)
                    background_tasks.add_task(
                        chunk_enrichment_service.enrich_all_chunks_background,
                        job_id=enrichment_job['id'],
                        knowledge_entry_id=source_id,
                        prompt_template=None,
                        ai_model=None,
                        chatbot_id=chatbox_id_str,
                        user_id=current_user["id"]
                    )

                    print(f"✅ [create_edited_pdf] AI enrichment job {enrichment_job['id']} başlatıldı")

                # Status'u processed yap
                supabase.table("knowledge_base_entries").update({
                    "status": "processed"
                }).eq("id", source_id).execute()

                created_entry["status"] = "processed"

        except Exception as process_error:
            print(f"⚠️ [create_edited_pdf] Otomatik işleme hatası: {str(process_error)}")
            # Hata olsa bile PDF oluşturuldu, sadece işleme başarısız
            supabase.table("knowledge_base_entries").update({
                "status": "failed",
                "error_message": f"Auto-processing failed: {str(process_error)}"
            }).eq("id", source_id).execute()

        return KnowledgeSourceResponse(**created_entry)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create edited PDF: {str(e)}"
        )


# ============================================================================
# PHASE 5: STATISTICS
# ============================================================================

@router.get("/{chatbox_id}/stats", response_model=ChatboxStats)
async def get_chatbox_stats(
    chatbox_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get comprehensive statistics for a chatbox

    - Conversation and message counts
    - Average response latency
    - Feedback and ratings
    - Sentiment distribution
    - Daily conversation trends
    - Related counts (stores, products, knowledge sources)
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        chatbox_id_str = str(chatbox_id)

        # Get conversation count
        conversation_result = supabase.table("conversations").select(
            "id", count="exact"
        ).eq("chatbot_id", chatbox_id_str).execute()
        total_conversations = conversation_result.count if conversation_result.count else 0

        # Get message count (sum of total_messages from conversations)
        messages_result = supabase.table("conversations").select(
            "total_messages"
        ).eq("chatbot_id", chatbox_id_str).execute()
        total_messages = sum(
            conv.get('total_messages', 0) for conv in messages_result.data
        ) if messages_result.data else 0

        # Get average latency
        latency_result = supabase.table("conversations").select(
            "avg_latency_ms"
        ).eq("chatbot_id", chatbox_id_str).execute()

        latencies = [
            conv['avg_latency_ms'] for conv in latency_result.data
            if conv.get('avg_latency_ms') is not None
        ] if latency_result.data else []
        avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0.0

        # Get feedback count and average rating
        feedback_result = supabase.table("chatbox_feedback").select(
            "rating, sentiment"
        ).eq("chatbox_id", chatbox_id_str).execute()

        total_feedback = len(feedback_result.data) if feedback_result.data else 0

        ratings = [
            fb['rating'] for fb in feedback_result.data
            if fb.get('rating') is not None
        ] if feedback_result.data else []
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        # Get sentiment distribution
        sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        if feedback_result.data:
            for fb in feedback_result.data:
                sentiment = fb.get('sentiment')
                if sentiment in sentiment_distribution:
                    sentiment_distribution[sentiment] += 1

        # Get store, product, knowledge source counts
        store_count_result = supabase.table("chatbox_stores").select(
            "id", count="exact"
        ).eq("chatbox_id", chatbox_id_str).execute()
        store_count = store_count_result.count if store_count_result.count else 0

        product_count_result = supabase.table("chatbox_products").select(
            "id", count="exact"
        ).eq("chatbox_id", chatbox_id_str).execute()
        product_count = product_count_result.count if product_count_result.count else 0

        knowledge_result = supabase.table("knowledge_base_entries").select(
            "token_count", count="exact"
        ).eq("chatbot_id", chatbox_id_str).execute()
        knowledge_source_count = knowledge_result.count if knowledge_result.count else 0

        total_tokens = sum(
            ks.get('token_count', 0) for ks in knowledge_result.data
        ) if knowledge_result.data else 0

        # Get daily conversations for the last N days
        # TODO: Implement date filtering when needed
        # For now, return empty array
        daily_conversations = []

        return ChatboxStats(
            total_conversations=total_conversations,
            total_messages=total_messages,
            avg_latency_ms=avg_latency_ms,
            avg_rating=avg_rating,
            total_feedback=total_feedback,
            store_count=store_count,
            product_count=product_count,
            knowledge_source_count=knowledge_source_count,
            total_tokens=total_tokens,
            sentiment_distribution=sentiment_distribution,
            daily_conversations=daily_conversations
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chatbox statistics: {str(e)}"
        )


# ============================================================================
# CHATBOX INTEGRATIONS (STORES & PRODUCTS)
# ============================================================================

@router.get("/integrations/all")
async def get_all_chatbox_integrations(
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get all chatbox integrations for the current user
    Returns: {
        "chatbox_id": {
            "chatbox_name": str,
            "stores": [store_id],
            "products": [product_id],
            "stores_only": [store_id]  # Sadece mağaza olarak işaretlenenler
        }
    }
    """
    try:
        # Get all user's chatboxes
        chatboxes_result = supabase.table("chatbots")\
            .select("id, name")\
            .eq("user_id", current_user["id"])\
            .execute()

        integrations = {}

        for chatbox in chatboxes_result.data:
            chatbox_id = chatbox["id"]

            # Get store integrations
            stores_result = supabase.table("chatbox_stores")\
                .select("store_id, show_on_products")\
                .eq("chatbox_id", chatbox_id)\
                .eq("is_active", True)\
                .execute()

            # Get product integrations
            products_result = supabase.table("chatbox_products")\
                .select("product_id")\
                .eq("chatbox_id", chatbox_id)\
                .eq("is_active", True)\
                .execute()

            stores = [rel["store_id"] for rel in stores_result.data]
            stores_only = [rel["store_id"] for rel in stores_result.data if not rel["show_on_products"]]

            # UNIQUE constraint ile artık her ürün sadece bir chatbox'ta olabilir
            # Bu yüzden TÜM ürünleri döndürüyoruz (filtreleme yok)
            products = [rel["product_id"] for rel in products_result.data]

            integrations[chatbox_id] = {
                "chatbox_name": chatbox["name"],
                "stores": stores,
                "products": products,  # TÜM ürünler (UNIQUE constraint sayesinde zaten tek chatbox'ta)
                "stores_only": stores_only
            }

        return integrations

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integrations: {str(e)}"
        )


@router.put("/{chatbox_id}/integrations", response_model=ChatboxIntegrationsResponse)
async def update_chatbox_integrations(
    chatbox_id: UUID,
    integrations: ChatboxIntegrationsUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update chatbox integrations (stores and products) - Replaces all existing integrations
    
    This endpoint:
    1. Verifies chatbox ownership
    2. Deletes all existing store and product integrations
    3. Creates new integrations based on the request
    4. Handles "stores_only" flag for stores without product display
    
    Args:
        chatbox_id: Chatbox UUID
        integrations: New integrations (stores and products)
        current_user: Authenticated user
        supabase: Supabase client
        
    Returns:
        Integration update summary with counts
    """
    try:
        # 1. Verify chatbox ownership
        chatbox_response = supabase.table("chatbots")\
            .select("id, user_id")\
            .eq("id", str(chatbox_id))\
            .single()\
            .execute()
        
        if not chatbox_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbox not found"
            )
        
        if chatbox_response.data["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this chatbox"
            )
        
        # 2. Delete existing integrations
        # Delete store integrations
        supabase.table("chatbox_stores")\
            .delete()\
            .eq("chatbox_id", str(chatbox_id))\
            .execute()
        
        # Delete product integrations
        supabase.table("chatbox_products")\
            .delete()\
            .eq("chatbox_id", str(chatbox_id))\
            .execute()
        
        # 3. Create new store integrations
        stores_added = 0

        if integrations.stores:
            store_records = []
            for store_integration in integrations.stores:
                store_records.append({
                    "chatbox_id": str(chatbox_id),
                    "store_id": str(store_integration.store_id),
                    "show_on_homepage": True,  # Mağaza her zaman ana sayfada gösterilir
                    "show_on_products": False,  # Mağaza seçimi ürün sayfalarında gösterilmez (sadece ürün seçimi yapılırsa gösterilir)
                    "position": store_integration.position,
                    "is_active": store_integration.is_active
                })
            
            if store_records:
                result = supabase.table("chatbox_stores")\
                    .insert(store_records)\
                    .execute()
                stores_added = len(result.data) if result.data else 0
        
        # 4. Create new product integrations
        products_added = 0
        if integrations.products:
            # Get all products that are used in OTHER chatboxes (not this one)
            other_chatbox_products = supabase.table("chatbox_products").select(
                "product_id, chatbox_id, chatbots!inner(name)"
            ).execute()

            # Create a map of product_id -> chatbox_name for products in OTHER chatboxes
            other_products_map = {}
            if other_chatbox_products.data:
                for item in other_chatbox_products.data:
                    # Since we deleted this chatbox's products, all remaining are from other chatboxes
                    other_products_map[item['product_id']] = item['chatbots']['name']

            product_records = []
            for product_integration in integrations.products:
                product_id_str = str(product_integration.product_id)

                # Check if product is used in another chatbox
                if product_id_str in other_products_map:
                    existing_chatbox = other_products_map[product_id_str]
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ürün '{product_id_str}' zaten '{existing_chatbox}' chatbox'ında kullanılıyor"
                    )

                product_records.append({
                    "chatbox_id": str(chatbox_id),
                    "product_id": product_id_str,
                    "show_on_product_page": product_integration.show_on_product_page,  # Frontend'den gelen değer
                    "show_on_store_homepage": product_integration.show_on_store_homepage,  # Frontend'den gelen değer (yeni sistemde False)
                    "is_active": product_integration.is_active
                })

            if product_records:
                result = supabase.table("chatbox_products")\
                    .insert(product_records)\
                    .execute()
                products_added = len(result.data) if result.data else 0

        # 5. Automatically activate chatbox when integrations are added
        if stores_added > 0 or products_added > 0:
            supabase.table("chatbots")\
                .update({"status": "active"})\
                .eq("id", str(chatbox_id))\
                .execute()

        return ChatboxIntegrationsResponse(
            stores_added=stores_added,
            products_added=products_added,
            stores_removed=0,  # We delete all before adding
            products_removed=0,  # We delete all before adding
            message=f"Successfully updated integrations: {stores_added} stores and {products_added} products"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integrations: {str(e)}"
        )


# ============================================================================
# KNOWLEDGE CHUNKS ENDPOINTS
# ============================================================================

@router.post("/{chatbox_id}/knowledge-sources/{source_id}/process-chunks", response_model=ProcessChunksResponse)
async def process_knowledge_chunks(
    chatbox_id: UUID,
    source_id: UUID,
    request: ProcessChunksRequest = ProcessChunksRequest(),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Process PDF text into chunks and store in knowledge_chunks table

    - Splits text into semantic chunks with overlap
    - Stores chunks with metadata
    - Returns statistics about chunking process
    """
    start_time = time.time()

    try:
        # 1. Verify chatbox ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # 2. Get knowledge source
        source_result = supabase.table("knowledge_base_entries").select(
            "id, source_name, content, status"
        ).eq("id", str(source_id)).eq("chatbot_id", str(chatbox_id)).execute()

        if not source_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )

        source = source_result.data[0]

        # 3. Validate content exists
        if not source.get("content"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Knowledge source has no content. Please upload and process the PDF first."
            )

        # 4. Check if chunks already exist
        existing_chunks = supabase.table("knowledge_chunks").select(
            "id", count="exact"
        ).eq("knowledge_entry_id", str(source_id)).execute()

        if existing_chunks.count and existing_chunks.count > 0 and not request.force_reprocess:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Chunks already exist for this source ({existing_chunks.count} chunks). Use force_reprocess=true to recreate."
            )

        # 5. Delete existing chunks if force reprocess
        if request.force_reprocess:
            supabase.table("knowledge_chunks").delete().eq(
                "knowledge_entry_id", str(source_id)
            ).execute()

        # 6. Create chunking service with custom parameters
        from ..services.chunking_service import ChunkingService
        chunker = ChunkingService(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            min_chunk_size=100
        )

        # 7. Chunk the text
        chunks = chunker.chunk_text(
            text=source["content"],
            source_name=source.get("source_name", "")
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create chunks from content"
            )

        # 8. Prepare chunk records for database
        chunk_records = []
        for chunk in chunks:
            chunk_records.append({
                "knowledge_entry_id": str(source_id),
                "chatbot_id": str(chatbox_id),
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "token_count": chunk["token_count"],
                "metadata": chunk["metadata"]
            })

        # 9. Batch insert chunks
        insert_result = supabase.table("knowledge_chunks").insert(chunk_records).execute()

        if not insert_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to insert chunks into database"
            )

        # 10. Calculate statistics
        stats = chunker.get_chunk_statistics(chunks)

        # 11. Create preview of first 3 chunks
        chunks_preview = []
        for chunk_data in insert_result.data[:3]:
            content_preview = chunk_data["content"][:100] + "..." if len(chunk_data["content"]) > 100 else chunk_data["content"]
            chunks_preview.append(ChunkListItem(
                id=chunk_data["id"],
                chunk_index=chunk_data["chunk_index"],
                content_preview=content_preview,
                token_count=chunk_data["token_count"],
                metadata=chunk_data["metadata"]
            ))

        # 12. Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        return ProcessChunksResponse(
            success=True,
            source_id=source_id,
            chunks_created=stats["total_chunks"],
            total_tokens=stats["total_tokens"],
            average_chunk_size=stats["average_chunk_size"],
            processing_time_ms=processing_time_ms,
            chunks_preview=chunks_preview
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chunks: {str(e)}"
        )


@router.get("/{chatbox_id}/knowledge-sources/{source_id}/chunks", response_model=List[ChunkResponse])
async def get_knowledge_chunks(
    chatbox_id: UUID,
    source_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get all chunks for a knowledge source
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Verify source exists and belongs to chatbox
        source_result = supabase.table("knowledge_base_entries").select("id").eq(
            "id", str(source_id)
        ).eq("chatbot_id", str(chatbox_id)).execute()

        if not source_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge source not found"
            )

        # Get chunks
        chunks_result = supabase.table("knowledge_chunks").select("*").eq(
            "knowledge_entry_id", str(source_id)
        ).order("chunk_index", desc=False).execute()

        if not chunks_result.data:
            return []

        return [ChunkResponse(**chunk) for chunk in chunks_result.data]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chunks: {str(e)}"
        )


@router.get("/{chatbox_id}/knowledge-sources/{source_id}/chunks/stats", response_model=ChunkStatistics)
async def get_chunks_statistics(
    chatbox_id: UUID,
    source_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get statistics about chunks for a knowledge source
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Get chunks
        chunks_result = supabase.table("knowledge_chunks").select(
            "content, token_count"
        ).eq("knowledge_entry_id", str(source_id)).execute()

        if not chunks_result.data:
            return ChunkStatistics(
                total_chunks=0,
                total_tokens=0,
                average_chunk_size=0,
                min_chunk_size=0,
                max_chunk_size=0
            )

        # Calculate statistics
        chunk_sizes = [len(chunk["content"]) for chunk in chunks_result.data]
        total_tokens = sum(chunk["token_count"] for chunk in chunks_result.data)

        return ChunkStatistics(
            total_chunks=len(chunks_result.data),
            total_tokens=total_tokens,
            average_chunk_size=sum(chunk_sizes) // len(chunk_sizes) if chunk_sizes else 0,
            min_chunk_size=min(chunk_sizes) if chunk_sizes else 0,
            max_chunk_size=max(chunk_sizes) if chunk_sizes else 0
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chunk statistics: {str(e)}"
        )


@router.delete("/{chatbox_id}/knowledge-sources/{source_id}/chunks", response_model=StatusResponse)
async def delete_knowledge_chunks(
    chatbox_id: UUID,
    source_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete all chunks for a knowledge source
    """
    try:
        # Verify ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)

        # Delete chunks
        result = supabase.table("knowledge_chunks").delete().eq(
            "knowledge_entry_id", str(source_id)
        ).execute()

        deleted_count = len(result.data) if result.data else 0

        return StatusResponse(
            success=True,
            message=f"Successfully deleted {deleted_count} chunks"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chunks: {str(e)}"
        )


@router.post("/migrate-chunks", response_model=Dict[str, Any])
async def migrate_existing_pdfs_to_chunks(
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    ONE-TIME MIGRATION: Chunk all existing PDFs that don't have chunks yet

    This endpoint processes all PDF knowledge sources that haven't been chunked
    and creates chunks for them.
    """
    try:
        start_time = time.time()

        # Get all knowledge base entries for user's chatbots
        entries_result = supabase.table("knowledge_base_entries").select(
            "id, chatbot_id, source_name, content, chatbots!inner(brands!inner(user_id))"
        ).eq("chatbots.brands.user_id", current_user["id"]).execute()

        if not entries_result.data:
            return {
                "success": True,
                "message": "No PDFs found",
                "total_pdfs": 0,
                "chunked": 0,
                "already_chunked": 0,
                "failed": 0
            }

        total_pdfs = len(entries_result.data)
        already_chunked = 0
        successfully_chunked = 0
        failed = 0
        total_chunks_created = 0

        # Process each entry
        for entry in entries_result.data:
            source_id = entry["id"]
            chatbot_id = entry["chatbot_id"]
            source_name = entry.get("source_name", "unknown.pdf")
            content = entry.get("content")

            # Check if already chunked
            existing = supabase.table("knowledge_chunks").select(
                "id", count="exact"
            ).eq("knowledge_entry_id", source_id).execute()

            if existing.count and existing.count > 0:
                already_chunked += 1
                continue

            # Skip if no content
            if not content or len(content.strip()) < 100:
                failed += 1
                continue

            try:
                # Chunk the text
                chunks = chunking_service.chunk_text(
                    text=content,
                    source_name=source_name
                )

                if not chunks:
                    failed += 1
                    continue

                # Prepare chunk records
                chunk_records = []
                for chunk in chunks:
                    chunk_records.append({
                        "knowledge_entry_id": source_id,
                        "chatbot_id": chatbot_id,
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "token_count": chunk["token_count"],
                        "metadata": chunk["metadata"]
                    })

                # Insert chunks
                insert_result = supabase.table("knowledge_chunks").insert(chunk_records).execute()

                if insert_result.data:
                    chunks_count = len(insert_result.data)
                    total_chunks_created += chunks_count
                    successfully_chunked += 1
                else:
                    failed += 1

            except Exception:
                failed += 1

        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "success": True,
            "message": f"Migration completed: {successfully_chunked} PDFs chunked",
            "total_pdfs": total_pdfs,
            "chunked": successfully_chunked,
            "already_chunked": already_chunked,
            "failed": failed,
            "total_chunks_created": total_chunks_created,
            "processing_time_ms": processing_time_ms
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to migrate PDFs: {str(e)}"
        )


@router.post("/{chatbox_id}/assign-pending-pdfs", response_model=StatusResponse)
async def assign_pending_pdfs_to_chatbox(
    chatbox_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Assign user's pending PDFs (chatbot_id = NULL) to a specific chatbox

    - Used after chatbox creation to link uploaded PDFs
    - Updates both knowledge_base_entries and knowledge_chunks
    """
    try:
        print(f"🔍 Starting PDF assignment for chatbox {chatbox_id}")
        
        # Verify chatbox ownership
        await verify_chatbox_ownership(str(chatbox_id), current_user, supabase)
        print(f"✅ Chatbox ownership verified")

        # Get all pending knowledge entries (chatbot_id = NULL) created recently
        try:
            pending_pdfs = supabase.table("knowledge_base_entries").select(
                "id, source_name, created_at"
            ).is_("chatbot_id", "null").order("created_at", desc=True).limit(10).execute()
            print(f"📊 Found {len(pending_pdfs.data) if pending_pdfs.data else 0} pending PDFs")
        except Exception as query_error:
            print(f"❌ Query error: {str(query_error)}")
            raise

        if not pending_pdfs.data:
            return StatusResponse(
                success=True,
                message="No pending PDFs found to assign"
            )

        # Filter by user: Check if PDFs were created in the last 5 minutes (reasonable timeframe)
        from datetime import datetime, timedelta, timezone
        recent_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)

        pdf_ids = []
        for pdf in pending_pdfs.data:
            try:
                created_at_str = pdf['created_at']
                # Handle both formats: with Z or with +00:00
                if created_at_str.endswith('Z'):
                    created_at_str = created_at_str.replace('Z', '+00:00')
                created_at = datetime.fromisoformat(created_at_str)
                
                if created_at > recent_threshold:
                    pdf_ids.append(pdf['id'])
                    print(f"✅ PDF {pdf['source_name']} is recent, adding to assignment list")
            except Exception as parse_error:
                print(f"⚠️ Failed to parse date for PDF {pdf.get('id')}: {str(parse_error)}")
                continue

        if not pdf_ids:
            print(f"⚠️ No recent PDFs found (threshold: {recent_threshold})")
            return StatusResponse(
                success=True,
                message="No recent pending PDFs found to assign"
            )

        print(f"📝 Assigning {len(pdf_ids)} PDFs to chatbox {chatbox_id}")

        # Update knowledge_base_entries: Set chatbot_id
        update_result = supabase.table("knowledge_base_entries").update({
            "chatbot_id": str(chatbox_id)
        }).in_("id", pdf_ids).execute()

        updated_pdfs = len(update_result.data) if update_result.data else 0
        print(f"✅ Updated {updated_pdfs} PDFs")

        # Update knowledge_chunks: Set chatbot_id for chunks belonging to these PDFs
        chunks_update = supabase.table("knowledge_chunks").update({
            "chatbot_id": str(chatbox_id)
        }).in_("knowledge_entry_id", pdf_ids).execute()

        updated_chunks = len(chunks_update.data) if chunks_update.data else 0
        print(f"✅ Updated {updated_chunks} chunks")

        # Update enrichment jobs: Set chatbot_id
        jobs_update = supabase.table("chunk_enrichment_jobs").update({
            "chatbot_id": str(chatbox_id)
        }).in_("knowledge_entry_id", pdf_ids).execute()

        print(f"✅ Assigned {updated_pdfs} PDFs and {updated_chunks} chunks to chatbox {chatbox_id}")

        return StatusResponse(
            success=True,
            message=f"Successfully assigned {updated_pdfs} PDFs ({updated_chunks} chunks) to chatbox"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ CRITICAL ERROR in assign_pending_pdfs: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign pending PDFs: {str(e)}"
        )
