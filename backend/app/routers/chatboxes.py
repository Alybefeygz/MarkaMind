from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import secrets

from ..schemas.chatbox import (
    ChatboxResponse, ChatboxCreate, ChatboxUpdate, ChatboxList,
    ChatboxStoreRelation, ChatboxStoreRelationCreate, ChatboxStoreRelationUpdate,
    ChatboxProductRelation, ChatboxProductRelationCreate, ChatboxProductRelationUpdate,
    ChatboxStoreBulkCreate, ChatboxStoreBulkResponse,
    KnowledgeSourceResponse, KnowledgeSourceStatusResponse,
    ChatboxStats
)
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client

router = APIRouter(
    prefix="/chatboxes",
    tags=["Chatboxes"],
    responses={404: {"description": "Not found"}}
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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

        # Check if relation already exists
        existing_check = supabase.table("chatbox_products").select("id").eq(
            "chatbox_id", str(chatbox_id)
        ).eq("product_id", str(relation.product_id)).execute()

        if existing_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already added to this chatbox"
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

        # Get existing relations
        existing_result = supabase.table("chatbox_products").select("product_id").eq(
            "chatbox_id", str(chatbox_id)
        ).execute()

        existing_product_ids = {item['product_id'] for item in existing_result.data} if existing_result.data else set()

        success_count = 0
        failed_count = 0
        skipped_count = 0
        results = []

        for product in products_result.data:
            product_id = product['id']

            # Check if already exists
            if product_id in existing_product_ids:
                skipped_count += 1
                results.append({
                    "product_id": product_id,
                    "success": False,
                    "message": "Already added",
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

@router.post("/{chatbox_id}/knowledge-sources", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_source(
    chatbox_id: UUID,
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

        # Create database record
        knowledge_data = {
            "chatbox_id": str(chatbox_id),
            "source_type": "pdf",
            "source_name": file.filename,
            "storage_path": storage_path,
            "file_size": file_size,
            "status": "pending",
            "token_count": 0
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

        # TODO: Trigger vector embedding process here
        # This would typically involve:
        # 1. Extract text from PDF
        # 2. Chunk the text
        # 3. Generate embeddings using OpenAI/OpenRouter
        # 4. Store embeddings in vector database
        # 5. Update status to 'completed' and token_count

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
