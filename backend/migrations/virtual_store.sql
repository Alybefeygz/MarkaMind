-- ============================================================================
-- Virtual Store and Product Management Tables Migration
-- ============================================================================
-- Created: 2025-09-30
-- Description: Creates tables for managing virtual stores, products, images,
--              reviews, and chatbot integrations
-- ============================================================================

-- ============================================================================
-- 1. STORES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS stores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id uuid NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name text NOT NULL,
    slug text NOT NULL UNIQUE,
    logo text,
    status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive')),
    platform text CHECK (platform IN ('web', 'mobile', 'both')),
    primary_color text DEFAULT '#000000',
    secondary_color text DEFAULT '#FFFFFF',
    text_color text DEFAULT '#000000',
    description text,
    meta_title text,
    meta_description text,
    custom_domain text,
    settings jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ============================================================================
-- 2. PRODUCTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id uuid NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    name text NOT NULL,
    slug text NOT NULL,
    description text,
    short_description text,
    price numeric(10, 2) NOT NULL CHECK (price >= 0),
    compare_at_price numeric(10, 2) CHECK (compare_at_price IS NULL OR compare_at_price >= price),
    cost_price numeric(10, 2) CHECK (cost_price IS NULL OR cost_price >= 0),
    category text NOT NULL,
    subcategory text,
    sku text,
    barcode text,
    stock_quantity integer DEFAULT 0 CHECK (stock_quantity >= 0),
    track_inventory boolean DEFAULT true,
    allow_backorder boolean DEFAULT false,
    weight numeric(10, 3) CHECK (weight IS NULL OR weight >= 0),
    dimensions jsonb DEFAULT '{}',
    status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    featured boolean DEFAULT false,
    tags text[] DEFAULT '{}',
    meta_title text,
    meta_description text,
    average_rating numeric(3, 2) DEFAULT 0.00 CHECK (average_rating >= 0 AND average_rating <= 5),
    review_count integer DEFAULT 0 CHECK (review_count >= 0),
    view_count integer DEFAULT 0 CHECK (view_count >= 0),
    sales_count integer DEFAULT 0 CHECK (sales_count >= 0),
    seo_data jsonb DEFAULT '{}',
    custom_fields jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(store_id, slug)
);

-- ============================================================================
-- 3. PRODUCT_IMAGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_images (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id uuid NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url text NOT NULL,
    alt_text text,
    display_order integer NOT NULL DEFAULT 0,
    is_primary boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ============================================================================
-- 4. PRODUCT_REVIEWS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_reviews (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id uuid NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    reviewer_name text NOT NULL,
    reviewer_email text,
    rating integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title text,
    comment text NOT NULL,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    verified_purchase boolean DEFAULT false,
    helpful_count integer DEFAULT 0 CHECK (helpful_count >= 0),
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ============================================================================
-- 5. CHATBOT_STORE_INTEGRATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS chatbot_store_integrations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    chatbot_id uuid NOT NULL REFERENCES chatbots(id) ON DELETE CASCADE,
    store_id uuid NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    is_active boolean DEFAULT true,
    settings jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(chatbot_id, store_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Stores indexes
CREATE INDEX IF NOT EXISTS idx_stores_brand_id ON stores(brand_id);
CREATE INDEX IF NOT EXISTS idx_stores_slug ON stores(slug);
CREATE INDEX IF NOT EXISTS idx_stores_status ON stores(status);
CREATE INDEX IF NOT EXISTS idx_stores_created_at ON stores(created_at DESC);

-- Products indexes
CREATE INDEX IF NOT EXISTS idx_products_store_id ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_featured ON products(featured) WHERE featured = true;
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku) WHERE sku IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_average_rating ON products(average_rating DESC);
CREATE INDEX IF NOT EXISTS idx_products_sales_count ON products(sales_count DESC);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);

-- Product images indexes
CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);
CREATE INDEX IF NOT EXISTS idx_product_images_display_order ON product_images(product_id, display_order);
CREATE INDEX IF NOT EXISTS idx_product_images_is_primary ON product_images(product_id, is_primary) WHERE is_primary = true;

-- Product reviews indexes
CREATE INDEX IF NOT EXISTS idx_product_reviews_product_id ON product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_user_id ON product_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_status ON product_reviews(status);
CREATE INDEX IF NOT EXISTS idx_product_reviews_rating ON product_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_product_reviews_created_at ON product_reviews(created_at DESC);

-- Chatbot store integrations indexes
CREATE INDEX IF NOT EXISTS idx_chatbot_store_integrations_chatbot_id ON chatbot_store_integrations(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_store_integrations_store_id ON chatbot_store_integrations(store_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_store_integrations_is_active ON chatbot_store_integrations(is_active) WHERE is_active = true;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE stores ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_store_integrations ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STORES RLS POLICIES
-- ============================================================================

-- Users can view stores of their own brands
DROP POLICY IF EXISTS stores_select_policy ON stores;
CREATE POLICY stores_select_policy ON stores
FOR SELECT
USING (
    brand_id IN (
        SELECT id FROM brands WHERE user_id = auth.uid()
    )
);

-- Users can insert stores for their own brands
DROP POLICY IF EXISTS stores_insert_policy ON stores;
CREATE POLICY stores_insert_policy ON stores
FOR INSERT
WITH CHECK (
    brand_id IN (
        SELECT id FROM brands WHERE user_id = auth.uid()
    )
);

-- Users can update stores of their own brands
DROP POLICY IF EXISTS stores_update_policy ON stores;
CREATE POLICY stores_update_policy ON stores
FOR UPDATE
USING (
    brand_id IN (
        SELECT id FROM brands WHERE user_id = auth.uid()
    )
);

-- Users can delete stores of their own brands
DROP POLICY IF EXISTS stores_delete_policy ON stores;
CREATE POLICY stores_delete_policy ON stores
FOR DELETE
USING (
    brand_id IN (
        SELECT id FROM brands WHERE user_id = auth.uid()
    )
);

-- ============================================================================
-- PRODUCTS RLS POLICIES
-- ============================================================================

-- Users can view products of their own stores
DROP POLICY IF EXISTS products_select_policy ON products;
CREATE POLICY products_select_policy ON products
FOR SELECT
USING (
    store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can insert products for their own stores
DROP POLICY IF EXISTS products_insert_policy ON products;
CREATE POLICY products_insert_policy ON products
FOR INSERT
WITH CHECK (
    store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can update products of their own stores
DROP POLICY IF EXISTS products_update_policy ON products;
CREATE POLICY products_update_policy ON products
FOR UPDATE
USING (
    store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can delete products of their own stores
DROP POLICY IF EXISTS products_delete_policy ON products;
CREATE POLICY products_delete_policy ON products
FOR DELETE
USING (
    store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- ============================================================================
-- PRODUCT_IMAGES RLS POLICIES
-- ============================================================================

-- Users can view images of their own products
DROP POLICY IF EXISTS product_images_select_policy ON product_images;
CREATE POLICY product_images_select_policy ON product_images
FOR SELECT
USING (
    product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can insert images for their own products
DROP POLICY IF EXISTS product_images_insert_policy ON product_images;
CREATE POLICY product_images_insert_policy ON product_images
FOR INSERT
WITH CHECK (
    product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can update images of their own products
DROP POLICY IF EXISTS product_images_update_policy ON product_images;
CREATE POLICY product_images_update_policy ON product_images
FOR UPDATE
USING (
    product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can delete images of their own products
DROP POLICY IF EXISTS product_images_delete_policy ON product_images;
CREATE POLICY product_images_delete_policy ON product_images
FOR DELETE
USING (
    product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- ============================================================================
-- PRODUCT_REVIEWS RLS POLICIES
-- ============================================================================

-- Users can view all reviews for their products
DROP POLICY IF EXISTS product_reviews_select_policy ON product_reviews;
CREATE POLICY product_reviews_select_policy ON product_reviews
FOR SELECT
USING (
    product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
    OR user_id = auth.uid()
);

-- Users can insert reviews for any product (public review submission)
DROP POLICY IF EXISTS product_reviews_insert_policy ON product_reviews;
CREATE POLICY product_reviews_insert_policy ON product_reviews
FOR INSERT
WITH CHECK (true);

-- Users can update their own reviews or reviews on their products
DROP POLICY IF EXISTS product_reviews_update_policy ON product_reviews;
CREATE POLICY product_reviews_update_policy ON product_reviews
FOR UPDATE
USING (
    user_id = auth.uid()
    OR product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can delete their own reviews or reviews on their products
DROP POLICY IF EXISTS product_reviews_delete_policy ON product_reviews;
CREATE POLICY product_reviews_delete_policy ON product_reviews
FOR DELETE
USING (
    user_id = auth.uid()
    OR product_id IN (
        SELECT p.id FROM products p
        INNER JOIN stores s ON p.store_id = s.id
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- ============================================================================
-- CHATBOT_STORE_INTEGRATIONS RLS POLICIES
-- ============================================================================

-- Users can view integrations for their own chatbots and stores
DROP POLICY IF EXISTS chatbot_store_integrations_select_policy ON chatbot_store_integrations;
CREATE POLICY chatbot_store_integrations_select_policy ON chatbot_store_integrations
FOR SELECT
USING (
    chatbot_id IN (
        SELECT id FROM chatbots WHERE brand_id IN (
            SELECT id FROM brands WHERE user_id = auth.uid()
        )
    )
    OR store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can insert integrations for their own chatbots and stores
DROP POLICY IF EXISTS chatbot_store_integrations_insert_policy ON chatbot_store_integrations;
CREATE POLICY chatbot_store_integrations_insert_policy ON chatbot_store_integrations
FOR INSERT
WITH CHECK (
    chatbot_id IN (
        SELECT id FROM chatbots WHERE brand_id IN (
            SELECT id FROM brands WHERE user_id = auth.uid()
        )
    )
    AND store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can update integrations for their own chatbots and stores
DROP POLICY IF EXISTS chatbot_store_integrations_update_policy ON chatbot_store_integrations;
CREATE POLICY chatbot_store_integrations_update_policy ON chatbot_store_integrations
FOR UPDATE
USING (
    chatbot_id IN (
        SELECT id FROM chatbots WHERE brand_id IN (
            SELECT id FROM brands WHERE user_id = auth.uid()
        )
    )
    AND store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- Users can delete integrations for their own chatbots and stores
DROP POLICY IF EXISTS chatbot_store_integrations_delete_policy ON chatbot_store_integrations;
CREATE POLICY chatbot_store_integrations_delete_policy ON chatbot_store_integrations
FOR DELETE
USING (
    chatbot_id IN (
        SELECT id FROM chatbots WHERE brand_id IN (
            SELECT id FROM brands WHERE user_id = auth.uid()
        )
    )
    AND store_id IN (
        SELECT s.id FROM stores s
        INNER JOIN brands b ON s.brand_id = b.id
        WHERE b.user_id = auth.uid()
    )
);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT COLUMNS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Stores trigger
DROP TRIGGER IF EXISTS update_stores_updated_at ON stores;
CREATE TRIGGER update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Products trigger
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Product images trigger
DROP TRIGGER IF EXISTS update_product_images_updated_at ON product_images;
CREATE TRIGGER update_product_images_updated_at
    BEFORE UPDATE ON product_images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Product reviews trigger
DROP TRIGGER IF EXISTS update_product_reviews_updated_at ON product_reviews;
CREATE TRIGGER update_product_reviews_updated_at
    BEFORE UPDATE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Chatbot store integrations trigger
DROP TRIGGER IF EXISTS update_chatbot_store_integrations_updated_at ON chatbot_store_integrations;
CREATE TRIGGER update_chatbot_store_integrations_updated_at
    BEFORE UPDATE ON chatbot_store_integrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TRIGGER FUNCTION FOR PRODUCT RATING AGGREGATION
-- ============================================================================

-- Function to update product average rating and review count
CREATE OR REPLACE FUNCTION update_product_rating_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products
    SET
        average_rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM product_reviews
            WHERE product_id = COALESCE(NEW.product_id, OLD.product_id)
            AND status = 'approved'
        ),
        review_count = (
            SELECT COUNT(*)
            FROM product_reviews
            WHERE product_id = COALESCE(NEW.product_id, OLD.product_id)
            AND status = 'approved'
        )
    WHERE id = COALESCE(NEW.product_id, OLD.product_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Trigger to update product stats when review is added/updated/deleted
DROP TRIGGER IF EXISTS update_product_rating_on_review_insert ON product_reviews;
CREATE TRIGGER update_product_rating_on_review_insert
    AFTER INSERT ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_rating_stats();

DROP TRIGGER IF EXISTS update_product_rating_on_review_update ON product_reviews;
CREATE TRIGGER update_product_rating_on_review_update
    AFTER UPDATE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_rating_stats();

DROP TRIGGER IF EXISTS update_product_rating_on_review_delete ON product_reviews;
CREATE TRIGGER update_product_rating_on_review_delete
    AFTER DELETE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_rating_stats();

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================