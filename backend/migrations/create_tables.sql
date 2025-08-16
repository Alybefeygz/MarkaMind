-- MarkaMind Database Schema
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable Row Level Security extension
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ================================
-- USERS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- BRANDS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    theme_color TEXT DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- CHATBOTS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.chatbots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES public.brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    avatar_url TEXT,
    primary_color TEXT DEFAULT '#3B82F6',
    secondary_color TEXT DEFAULT '#EF4444',
    animation_style TEXT DEFAULT 'fade',
    script_token TEXT UNIQUE NOT NULL DEFAULT uuid_generate_v4()::TEXT,
    language TEXT DEFAULT 'tr' CHECK (language IN ('tr', 'en', 'de', 'fr', 'es')),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- KNOWLEDGE BASE ENTRIES TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.knowledge_base_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('manual', 'pdf', 'url', 'txt')),
    source_url TEXT,
    content TEXT,
    embedding_id TEXT,
    token_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'ready', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- CHAT PROMPTS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.chat_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    temperature FLOAT DEFAULT 0.7 CHECK (temperature >= 0.0 AND temperature <= 1.0),
    context_size INTEGER DEFAULT 2000,
    top_p FLOAT DEFAULT 0.9 CHECK (top_p >= 0.0 AND top_p <= 1.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- CONVERSATIONS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL,
    user_input TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    source_entry_id UUID REFERENCES public.knowledge_base_entries(id),
    latency_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- FEEDBACK TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- UPLOADS TABLE
-- ================================
CREATE TABLE IF NOT EXISTS public.uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    storage_url TEXT NOT NULL,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- Brands indexes
CREATE INDEX IF NOT EXISTS idx_brands_user_id ON public.brands(user_id);
CREATE INDEX IF NOT EXISTS idx_brands_slug ON public.brands(slug);
CREATE INDEX IF NOT EXISTS idx_brands_is_active ON public.brands(is_active);

-- Chatbots indexes
CREATE INDEX IF NOT EXISTS idx_chatbots_brand_id ON public.chatbots(brand_id);
CREATE INDEX IF NOT EXISTS idx_chatbots_script_token ON public.chatbots(script_token);
CREATE INDEX IF NOT EXISTS idx_chatbots_status ON public.chatbots(status);

-- Knowledge base indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_chatbot_id ON public.knowledge_base_entries(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_type ON public.knowledge_base_entries(source_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_status ON public.knowledge_base_entries(status);

-- Chat prompts indexes
CREATE INDEX IF NOT EXISTS idx_chat_prompts_chatbot_id ON public.chat_prompts(chatbot_id);

-- Conversations indexes
CREATE INDEX IF NOT EXISTS idx_conversations_chatbot_id ON public.conversations(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON public.conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON public.conversations(created_at);

-- Feedback indexes
CREATE INDEX IF NOT EXISTS idx_feedback_conversation_id ON public.feedback(conversation_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON public.feedback(rating);

-- Uploads indexes
CREATE INDEX IF NOT EXISTS idx_uploads_chatbot_id ON public.uploads(chatbot_id);
CREATE INDEX IF NOT EXISTS idx_uploads_processed ON public.uploads(processed);

-- ================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chatbots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_base_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploads ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- Brands policies
CREATE POLICY "Users can view own brands" ON public.brands
    FOR SELECT USING (auth.uid()::TEXT = user_id::TEXT);

CREATE POLICY "Users can create own brands" ON public.brands
    FOR INSERT WITH CHECK (auth.uid()::TEXT = user_id::TEXT);

CREATE POLICY "Users can update own brands" ON public.brands
    FOR UPDATE USING (auth.uid()::TEXT = user_id::TEXT);

CREATE POLICY "Users can delete own brands" ON public.brands
    FOR DELETE USING (auth.uid()::TEXT = user_id::TEXT);

-- Chatbots policies
CREATE POLICY "Users can view own chatbots" ON public.chatbots
    FOR SELECT USING (brand_id IN (
        SELECT id FROM public.brands WHERE user_id::TEXT = auth.uid()::TEXT
    ));

CREATE POLICY "Users can create chatbots for own brands" ON public.chatbots
    FOR INSERT WITH CHECK (brand_id IN (
        SELECT id FROM public.brands WHERE user_id::TEXT = auth.uid()::TEXT
    ));

CREATE POLICY "Users can update own chatbots" ON public.chatbots
    FOR UPDATE USING (brand_id IN (
        SELECT id FROM public.brands WHERE user_id::TEXT = auth.uid()::TEXT
    ));

CREATE POLICY "Users can delete own chatbots" ON public.chatbots
    FOR DELETE USING (brand_id IN (
        SELECT id FROM public.brands WHERE user_id::TEXT = auth.uid()::TEXT
    ));

-- Public access for published chatbots via script_token
CREATE POLICY "Public can access published chatbots" ON public.chatbots
    FOR SELECT USING (status = 'published');

-- Knowledge base entries policies
CREATE POLICY "Users can manage knowledge for own chatbots" ON public.knowledge_base_entries
    FOR ALL USING (chatbot_id IN (
        SELECT c.id FROM public.chatbots c
        JOIN public.brands b ON c.brand_id = b.id
        WHERE b.user_id::TEXT = auth.uid()::TEXT
    ));

-- Chat prompts policies
CREATE POLICY "Users can manage prompts for own chatbots" ON public.chat_prompts
    FOR ALL USING (chatbot_id IN (
        SELECT c.id FROM public.chatbots c
        JOIN public.brands b ON c.brand_id = b.id
        WHERE b.user_id::TEXT = auth.uid()::TEXT
    ));

-- Conversations policies (allow public for widget usage)
CREATE POLICY "Allow conversations for published chatbots" ON public.conversations
    FOR INSERT WITH CHECK (chatbot_id IN (
        SELECT id FROM public.chatbots WHERE status = 'published'
    ));

CREATE POLICY "Users can view conversations for own chatbots" ON public.conversations
    FOR SELECT USING (chatbot_id IN (
        SELECT c.id FROM public.chatbots c
        JOIN public.brands b ON c.brand_id = b.id
        WHERE b.user_id::TEXT = auth.uid()::TEXT
    ));

-- Feedback policies (allow public)
CREATE POLICY "Allow feedback for all conversations" ON public.feedback
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view feedback for own chatbots" ON public.feedback
    FOR SELECT USING (conversation_id IN (
        SELECT conv.id FROM public.conversations conv
        JOIN public.chatbots c ON conv.chatbot_id = c.id
        JOIN public.brands b ON c.brand_id = b.id
        WHERE b.user_id::TEXT = auth.uid()::TEXT
    ));

-- Uploads policies
CREATE POLICY "Users can manage uploads for own chatbots" ON public.uploads
    FOR ALL USING (chatbot_id IN (
        SELECT c.id FROM public.chatbots c
        JOIN public.brands b ON c.brand_id = b.id
        WHERE b.user_id::TEXT = auth.uid()::TEXT
    ));

-- ================================
-- TRIGGER FUNCTIONS FOR UPDATED_AT
-- ================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_brands_updated_at 
    BEFORE UPDATE ON public.brands 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_chatbots_updated_at 
    BEFORE UPDATE ON public.chatbots 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_knowledge_base_entries_updated_at 
    BEFORE UPDATE ON public.knowledge_base_entries 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_chat_prompts_updated_at 
    BEFORE UPDATE ON public.chat_prompts 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_uploads_updated_at 
    BEFORE UPDATE ON public.uploads 
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- ================================
-- SAMPLE DATA (Optional)
-- ================================

-- Insert sample user (for testing)
-- INSERT INTO public.users (email, full_name, role) 
-- VALUES ('test@markamind.com', 'Test User', 'user')
-- ON CONFLICT (email) DO NOTHING;