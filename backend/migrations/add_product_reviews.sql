-- ============================================================================
-- Product Reviews Migration
-- ============================================================================
-- This migration creates the product_reviews table and updates the products table
-- to track review statistics
-- ============================================================================

-- Step 1: Ensure products table has review tracking columns
-- ----------------------------------------------------------------------------
ALTER TABLE products
ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS average_rating NUMERIC(3, 2) DEFAULT 0.00 NOT NULL;

-- Add constraints
ALTER TABLE products
ADD CONSTRAINT check_average_rating CHECK (average_rating >= 0 AND average_rating <= 5);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_review_count ON products(review_count);
CREATE INDEX IF NOT EXISTS idx_products_average_rating ON products(average_rating);


-- Step 2: Create product_reviews table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Review content
    reviewer_name VARCHAR(100) NOT NULL,
    reviewer_email VARCHAR(200),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    comment TEXT NOT NULL,

    -- Review metadata
    verified_purchase BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    helpful_count INTEGER DEFAULT 0 NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for product_reviews
CREATE INDEX IF NOT EXISTS idx_product_reviews_product_id ON product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_user_id ON product_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_status ON product_reviews(status);
CREATE INDEX IF NOT EXISTS idx_product_reviews_rating ON product_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_product_reviews_created_at ON product_reviews(created_at DESC);


-- Step 3: Create trigger to auto-update products.updated_at
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_product_reviews_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_product_reviews_updated_at
    BEFORE UPDATE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_reviews_updated_at();


-- Step 4: Create function to update product review stats
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_product_review_stats()
RETURNS TRIGGER AS $$
DECLARE
    v_product_id UUID;
    v_review_count INTEGER;
    v_average_rating NUMERIC(3, 2);
BEGIN
    -- Determine product_id based on operation
    IF TG_OP = 'DELETE' THEN
        v_product_id := OLD.product_id;
    ELSE
        v_product_id := NEW.product_id;
    END IF;

    -- Calculate review stats for approved reviews only
    SELECT
        COUNT(*)::INTEGER,
        COALESCE(ROUND(AVG(rating)::NUMERIC, 2), 0.00)
    INTO
        v_review_count,
        v_average_rating
    FROM product_reviews
    WHERE product_id = v_product_id
    AND status = 'approved';

    -- Update product table
    UPDATE products
    SET
        review_count = v_review_count,
        average_rating = v_average_rating,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = v_product_id;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for review stats update
DROP TRIGGER IF EXISTS trigger_update_product_review_stats_insert ON product_reviews;
DROP TRIGGER IF EXISTS trigger_update_product_review_stats_update ON product_reviews;
DROP TRIGGER IF EXISTS trigger_update_product_review_stats_delete ON product_reviews;

CREATE TRIGGER trigger_update_product_review_stats_insert
    AFTER INSERT ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_review_stats();

CREATE TRIGGER trigger_update_product_review_stats_update
    AFTER UPDATE ON product_reviews
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status OR OLD.rating IS DISTINCT FROM NEW.rating)
    EXECUTE FUNCTION update_product_review_stats();

CREATE TRIGGER trigger_update_product_review_stats_delete
    AFTER DELETE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_product_review_stats();


-- Step 5: Enable Row Level Security (RLS)
-- ----------------------------------------------------------------------------
ALTER TABLE product_reviews ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read approved reviews
CREATE POLICY product_reviews_select_approved ON product_reviews
    FOR SELECT
    USING (status = 'approved');

-- Policy: Authenticated users can insert reviews
CREATE POLICY product_reviews_insert_policy ON product_reviews
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own pending reviews
CREATE POLICY product_reviews_update_own ON product_reviews
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id AND status = 'pending');

-- Policy: Store owners can update reviews for their products
CREATE POLICY product_reviews_update_owner ON product_reviews
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM products p
            INNER JOIN stores s ON p.store_id = s.id
            INNER JOIN brands b ON s.brand_id = b.id
            WHERE p.id = product_reviews.product_id
            AND b.user_id = auth.uid()
        )
    );

-- Policy: Users can delete their own reviews
CREATE POLICY product_reviews_delete_own ON product_reviews
    FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- Policy: Store owners can delete reviews for their products
CREATE POLICY product_reviews_delete_owner ON product_reviews
    FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM products p
            INNER JOIN stores s ON p.store_id = s.id
            INNER JOIN brands b ON s.brand_id = b.id
            WHERE p.id = product_reviews.product_id
            AND b.user_id = auth.uid()
        )
    );


-- Step 6: Add comments for documentation
-- ----------------------------------------------------------------------------
COMMENT ON TABLE product_reviews IS 'Product reviews and ratings from customers';
COMMENT ON COLUMN product_reviews.verified_purchase IS 'Whether the reviewer actually purchased the product';
COMMENT ON COLUMN product_reviews.status IS 'Review moderation status: pending, approved, or rejected';
COMMENT ON COLUMN product_reviews.helpful_count IS 'Number of users who found this review helpful';

COMMENT ON COLUMN products.review_count IS 'Total number of approved reviews';
COMMENT ON COLUMN products.average_rating IS 'Average rating from approved reviews (0-5)';
