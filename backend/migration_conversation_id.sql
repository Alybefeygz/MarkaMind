-- ============================================
-- ADIM 12: Chat Messages Conversation ID Migration
-- ============================================
-- Bu SQL'i Supabase Dashboard > SQL Editor'da çalıştırın

-- 1. Eski mesajlara conversation_id ekle (NULL olanlar için)
UPDATE chat_messages 
SET conversation_id = gen_random_uuid() 
WHERE conversation_id IS NULL;

-- 2. conversation_id kolonunu NOT NULL yap
ALTER TABLE chat_messages
ALTER COLUMN conversation_id SET NOT NULL;

-- ✅ Migration başarılı - conversation_id artık zorunlu!
