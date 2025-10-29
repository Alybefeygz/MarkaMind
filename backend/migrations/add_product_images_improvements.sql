-- Migration: Add improvements to product_images table
-- Date: 2025-09-30
-- Description: Add thumbnail_url and alt_text columns, plus performance indexes

-- 1. Add thumbnail_url column (if not exists)
-- This stores direct thumbnail URL for performance
ALTER TABLE product_images
ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;

-- 2. Add alt_text column (if not exists)
-- For SEO and accessibility
ALTER TABLE product_images
ADD COLUMN IF NOT EXISTS alt_text TEXT;

-- 3. Add performance index for primary image lookups
-- This speeds up queries that find the primary image for a product
CREATE INDEX IF NOT EXISTS idx_product_images_is_primary
ON product_images(product_id, is_primary)
WHERE is_primary = true;

-- 4. Add index for display order
-- This speeds up ordered image queries
CREATE INDEX IF NOT EXISTS idx_product_images_display_order
ON product_images(product_id, display_order);

-- 5. Add comment to columns
COMMENT ON COLUMN product_images.thumbnail_url IS 'Direct URL to 64x64 thumbnail image for performance';
COMMENT ON COLUMN product_images.alt_text IS 'Alternative text for image (SEO & accessibility)';
COMMENT ON COLUMN product_images.is_primary IS 'Flag indicating if this is the main/primary product image';
COMMENT ON COLUMN product_images.display_order IS 'Order in which images should be displayed (0-based)';

-- 6. Verify changes
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'product_images'
ORDER BY ordinal_position;
