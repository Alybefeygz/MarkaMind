from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..schemas.product import (
    ProductResponse, ProductCreate, ProductUpdate, ProductList,
    ProductPublic, ProductWithImages, ProductDetail,
    ProductImageResponse, ProductImageCreate, ProductImageUpdate,
    ProductReviewResponse, ProductReviewCreate, ProductReviewUpdate
)
from ..schemas.common import StatusResponse, PaginationParams, PaginationResponse
from ..dependencies import get_current_user, get_supabase_client
from ..services.product_image_service import product_image_service
from ..constants.mock_reviews import get_mock_reviews

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a new product for a store
    """
    try:
        # Verify store belongs to user through brand
        store_result = supabase.table("stores").select(
            "*, brands!inner(user_id)"
        ).eq("id", str(product.store_id)).eq("brands.user_id", current_user["id"]).execute()

        if not store_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found or you don't have permission"
            )

        # Check if slug is unique within the store
        slug_check = supabase.table("products").select("id").eq(
            "store_id", str(product.store_id)
        ).eq("slug", product.slug).execute()

        if slug_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this slug already exists in this store"
            )

        # Prepare product data
        product_data = product.model_dump()
        product_data["store_id"] = str(product.store_id)

        # Extract initial_review_count before inserting
        initial_review_count = product_data.pop("initial_review_count", 0)

        # Convert Decimal to string for PostgreSQL numeric type
        for field in ["price", "compare_at_price", "cost_price", "weight"]:
            if product_data.get(field) is not None:
                product_data[field] = str(product_data[field])

        # Create product in database
        result = supabase.table("products").insert(product_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create product"
            )

        created_product = result.data[0]
        product_id = created_product["id"]

        # Create mock reviews if requested
        if initial_review_count > 0:
            mock_reviews = get_mock_reviews(initial_review_count)

            for review in mock_reviews:
                review_data = {
                    **review,
                    "product_id": product_id,
                    "user_id": current_user["id"]
                }
                supabase.table("product_reviews").insert(review_data).execute()

            # Update product's review_count
            supabase.table("products").update({
                "review_count": initial_review_count
            }).eq("id", product_id).execute()

            # Recalculate average rating
            total_rating = sum(r["rating"] for r in mock_reviews)
            average_rating = total_rating / initial_review_count if initial_review_count > 0 else 0

            supabase.table("products").update({
                "average_rating": str(average_rating)
            }).eq("id", product_id).execute()

            # Fetch updated product
            updated_result = supabase.table("products").select("*").eq("id", product_id).execute()
            if updated_result.data:
                created_product = updated_result.data[0]

        return ProductResponse(**created_product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("/", response_model=PaginationResponse[ProductList])
async def list_products(
    store_id: Optional[UUID] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    featured: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get list of user's products with pagination and filters
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size

        # Build query - get products through stores and brands
        query = supabase.table("products").select(
            "*, stores!inner(brand_id, brands!inner(user_id))",
            count="exact"
        ).eq("stores.brands.user_id", current_user["id"])

        # Apply filters
        if store_id:
            query = query.eq("store_id", str(store_id))
        if category:
            query = query.eq("category", category)
        if status_filter:
            query = query.eq("status", status_filter)
        if featured is not None:
            query = query.eq("featured", featured)
        if min_price is not None:
            query = query.gte("price", min_price)
        if max_price is not None:
            query = query.lte("price", max_price)

        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0

        # Get products with pagination
        query = query.order(pagination.sort or "created_at", desc=True)
        result = query.range(offset, offset + pagination.size - 1).execute()

        # Transform data - remove nested objects
        products_data = []
        for product in result.data if result.data else []:
            product_copy = product.copy()
            product_copy.pop('stores', None)
            products_data.append(ProductList(**product_copy))

        return PaginationResponse(
            items=products_data,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get products: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific product by ID
    """
    try:
        # Get product with store and brand user_id check
        result = supabase.table("products").select(
            "*, stores!inner(brand_id, brands!inner(user_id))"
        ).eq("id", str(product_id)).eq("stores.brands.user_id", current_user["id"]).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        product_data = result.data[0].copy()
        product_data.pop('stores', None)

        return ProductResponse(**product_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product: {str(e)}"
        )


@router.get("/{product_id}/detail", response_model=ProductDetail)
async def get_product_detail(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Get detailed product information including images and reviews
    """
    try:
        # Get product
        product_result = supabase.table("products").select(
            "*, stores!inner(brand_id, brands!inner(user_id))"
        ).eq("id", str(product_id)).eq("stores.brands.user_id", current_user["id"]).execute()

        if not product_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        product_data = product_result.data[0].copy()
        product_data.pop('stores', None)

        # Get images
        images_result = supabase.table("product_images").select("*").eq(
            "product_id", str(product_id)
        ).order("display_order").execute()

        images = [ProductImageResponse(**img) for img in images_result.data] if images_result.data else []

        # Get reviews
        reviews_result = supabase.table("product_reviews").select("*").eq(
            "product_id", str(product_id)
        ).order("created_at", desc=True).execute()

        reviews = [ProductReviewResponse(**rev) for rev in reviews_result.data] if reviews_result.data else []

        return ProductDetail(
            **product_data,
            images=images,
            reviews=reviews
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get product detail: {str(e)}"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update a specific product
    """
    try:
        # Check if product exists and belongs to user
        existing = supabase.table("products").select(
            "store_id, stores!inner(brand_id, brands!inner(user_id))"
        ).eq("id", str(product_id)).eq("stores.brands.user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        store_id = existing.data[0]["store_id"]

        # Check slug uniqueness if updating slug
        update_data = product_update.model_dump(exclude_unset=True)

        if "slug" in update_data:
            slug_check = supabase.table("products").select("id").eq(
                "store_id", store_id
            ).eq("slug", update_data["slug"]).neq("id", str(product_id)).execute()

            if slug_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this slug already exists in this store"
                )

        # Convert Decimal to string for PostgreSQL numeric type
        for field in ["price", "compare_at_price", "cost_price", "weight"]:
            if update_data.get(field) is not None:
                update_data[field] = str(update_data[field])

        # Update product
        result = supabase.table("products").update(update_data).eq("id", str(product_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update product"
            )

        return ProductResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete("/{product_id}", response_model=StatusResponse)
async def delete_product(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a specific product
    """
    try:
        # Check if product exists and belongs to user
        existing = supabase.table("products").select(
            "*, stores!inner(brand_id, brands!inner(user_id))"
        ).eq("id", str(product_id)).eq("stores.brands.user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Delete product (CASCADE will delete related images and reviews)
        result = supabase.table("products").delete().eq("id", str(product_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete product"
            )

        return StatusResponse(
            success=True,
            message="Product deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        )


# ============================================================================
# PRODUCT IMAGES ENDPOINTS
# ============================================================================

@router.post("/{product_id}/images")
async def add_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    display_order: int = 0,
    is_primary: bool = False,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Add single image to product

    - Validates product ownership
    - Uploads image to storage (4 sizes)
    - Creates database record
    """
    try:
        # Verify product belongs to user
        product_check = supabase.table("products").select(
            "*, stores!inner(brands!inner(user_id))"
        ).eq("id", str(product_id)).eq(
            "stores.brands.user_id", current_user["id"]
        ).execute()

        if not product_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or you don't have permission"
            )

        # Upload image
        result = await product_image_service.upload_image(
            product_id=str(product_id),
            file=file,
            display_order=display_order,
            is_primary=is_primary
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add image: {str(e)}"
        )


@router.post("/{product_id}/images/batch")
async def add_multiple_product_images(
    product_id: UUID,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Add multiple images to product at once

    - Max 10 images per product
    - First image becomes primary if no images exist
    - Returns list of upload results
    """
    try:
        # Verify product ownership
        product_check = supabase.table("products").select(
            "*, stores!inner(brands!inner(user_id))"
        ).eq("id", str(product_id)).eq(
            "stores.brands.user_id", current_user["id"]
        ).execute()

        if not product_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or you don't have permission"
            )

        # Upload images
        results = await product_image_service.upload_multiple_images(
            product_id=str(product_id),
            files=files
        )

        return {
            "success": True,
            "uploaded_count": len(results),
            "images": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add images: {str(e)}"
        )


@router.get("/{product_id}/images", response_model=List[ProductImageResponse])
async def get_product_images(
    product_id: UUID,
    supabase = Depends(get_supabase_client)
):
    """
    Get all images for a product (public endpoint)

    - Ordered by display_order
    - Includes all sizes
    """
    try:
        result = supabase.table("product_images").select("*").eq(
            "product_id", str(product_id)
        ).order("display_order").execute()

        return [ProductImageResponse(**img) for img in result.data] if result.data else []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get images: {str(e)}"
        )


@router.patch("/images/{image_id}/primary")
async def set_primary_image(
    image_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Set image as primary/main image

    - Validates ownership
    - Unsets other primary images
    - Returns success
    """
    try:
        # Verify image belongs to user's product
        image_check = supabase.table("product_images").select(
            "*, products!inner(stores!inner(brands!inner(user_id)))"
        ).eq("id", str(image_id)).eq(
            "products.stores.brands.user_id", current_user["id"]
        ).execute()

        if not image_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        # Set as primary
        result = await product_image_service.set_primary_image(str(image_id))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set primary image: {str(e)}"
        )


@router.patch("/{product_id}/images/reorder")
async def reorder_product_images(
    product_id: UUID,
    order_list: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Reorder product images

    Body format:
    [
        {"image_id": "uuid1", "display_order": 0},
        {"image_id": "uuid2", "display_order": 1},
        ...
    ]
    """
    try:
        # Verify product ownership
        product_check = supabase.table("products").select(
            "*, stores!inner(brands!inner(user_id))"
        ).eq("id", str(product_id)).eq(
            "stores.brands.user_id", current_user["id"]
        ).execute()

        if not product_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or you don't have permission"
            )

        # Reorder images
        result = await product_image_service.reorder_images(
            product_id=str(product_id),
            order_list=order_list
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder images: {str(e)}"
        )


@router.put("/images/{image_id}", response_model=ProductImageResponse)
async def update_product_image(
    image_id: UUID,
    image_update: ProductImageUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update product image metadata

    - Can update: alt_text, display_order, is_primary
    - Cannot update: actual image file (use delete + upload)
    """
    try:
        # Verify image belongs to user's product
        existing = supabase.table("product_images").select(
            "product_id, products!inner(stores!inner(brands!inner(user_id)))"
        ).eq("id", str(image_id)).eq(
            "products.stores.brands.user_id", current_user["id"]
        ).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        product_id = existing.data[0]["product_id"]
        update_data = image_update.model_dump(exclude_unset=True)

        # If setting as primary, unset others
        if update_data.get("is_primary"):
            await product_image_service._unset_other_primary_images(
                product_id, str(image_id)
            )

        # Update image
        result = supabase.table("product_images").update(update_data).eq(
            "id", str(image_id)
        ).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update image"
            )

        return ProductImageResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update image: {str(e)}"
        )


@router.delete("/images/{image_id}", response_model=StatusResponse)
async def delete_product_image(
    image_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete product image

    - Deletes from storage (all sizes)
    - Deletes from database
    - If was primary, sets another as primary
    """
    try:
        # Verify image belongs to user's product
        existing = supabase.table("product_images").select(
            "*, products!inner(stores!inner(brands!inner(user_id)))"
        ).eq("id", str(image_id)).eq(
            "products.stores.brands.user_id", current_user["id"]
        ).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        # Delete image
        result = await product_image_service.delete_image(str(image_id))

        return StatusResponse(
            success=True,
            message="Image deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )


# ============================================================================
# PRODUCT REVIEWS ENDPOINTS
# ============================================================================

@router.post("/{product_id}/reviews", response_model=ProductReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_product_review(
    product_id: UUID,
    review: ProductReviewCreate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Create a review for a product
    """
    try:
        # Check if product exists
        product_check = supabase.table("products").select("id").eq("id", str(product_id)).execute()

        if not product_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Prepare review data
        review_data = review.model_dump()
        review_data["product_id"] = str(product_id)
        review_data["user_id"] = current_user["id"]

        # Create review
        result = supabase.table("product_reviews").insert(review_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create review"
            )

        return ProductReviewResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


@router.get("/{product_id}/reviews", response_model=PaginationResponse[ProductReviewResponse])
async def get_product_reviews(
    product_id: UUID,
    status_filter: Optional[str] = Query("approved", pattern="^(pending|approved|rejected)$"),
    pagination: PaginationParams = Depends(),
    supabase = Depends(get_supabase_client)
):
    """
    Get reviews for a product (public endpoint)
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size

        # Build query
        query = supabase.table("product_reviews").select(
            "*", count="exact"
        ).eq("product_id", str(product_id))

        if status_filter:
            query = query.eq("status", status_filter)

        # Get total count
        count_result = query.execute()
        total = count_result.count if count_result.count else 0

        # Get reviews with pagination
        query = query.order("created_at", desc=True)
        result = query.range(offset, offset + pagination.size - 1).execute()

        reviews = [ProductReviewResponse(**rev) for rev in result.data] if result.data else []

        return PaginationResponse(
            items=reviews,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviews: {str(e)}"
        )


@router.patch("/reviews/{review_id}", response_model=ProductReviewResponse)
async def update_product_review_status(
    review_id: UUID,
    review_update: ProductReviewUpdate,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Update review status (admin/store owner only)
    """
    try:
        # Check if review belongs to user's product
        existing = supabase.table("product_reviews").select(
            "*, products!inner(stores!inner(brands!inner(user_id)))"
        ).eq("id", str(review_id)).eq(
            "products.stores.brands.user_id", current_user["id"]
        ).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Update review
        update_data = review_update.model_dump(exclude_unset=True)
        result = supabase.table("product_reviews").update(update_data).eq("id", str(review_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update review"
            )

        return ProductReviewResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update review: {str(e)}"
        )


@router.delete("/reviews/{review_id}", response_model=StatusResponse)
async def delete_product_review(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a review (owner or store owner)
    """
    try:
        # Check if review belongs to user or user's product
        existing = supabase.table("product_reviews").select(
            "user_id, products!inner(stores!inner(brands!inner(user_id)))"
        ).eq("id", str(review_id)).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        review_user_id = existing.data[0].get("user_id")
        store_owner_id = existing.data[0].get("products", {}).get("stores", {}).get("brands", {}).get("user_id")

        # User can delete if they own the review or the store
        if review_user_id != current_user["id"] and store_owner_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this review"
            )

        # Delete review
        result = supabase.table("product_reviews").delete().eq("id", str(review_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete review"
            )

        return StatusResponse(
            success=True,
            message="Review deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete review: {str(e)}"
        )