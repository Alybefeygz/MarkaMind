-- ============================================
-- Authentication Helper Functions
-- ============================================
-- Kullanışlı PostgreSQL fonksiyonları
-- ============================================

-- 1. Email verification token oluşturma fonksiyonu
CREATE OR REPLACE FUNCTION create_email_verification_token(
    p_user_id UUID,
    p_email TEXT,
    p_token_hash TEXT,
    p_client_ip INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_token_id UUID;
BEGIN
    INSERT INTO email_verification_tokens (
        user_id,
        email,
        token_hash,
        client_ip,
        user_agent,
        expires_at
    ) VALUES (
        p_user_id,
        p_email,
        p_token_hash,
        p_client_ip,
        p_user_agent,
        NOW() + INTERVAL '24 hours'
    )
    RETURNING id INTO v_token_id;

    RETURN v_token_id;
END;
$$ LANGUAGE plpgsql;

-- 2. Password reset token oluşturma fonksiyonu
CREATE OR REPLACE FUNCTION create_password_reset_token(
    p_user_id UUID,
    p_token_hash TEXT,
    p_client_ip INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_token_id UUID;
BEGIN
    INSERT INTO password_reset_tokens (
        user_id,
        token_hash,
        client_ip,
        user_agent,
        expires_at
    ) VALUES (
        p_user_id,
        p_token_hash,
        p_client_ip,
        p_user_agent,
        NOW() + INTERVAL '1 hour'
    )
    RETURNING id INTO v_token_id;

    RETURN v_token_id;
END;
$$ LANGUAGE plpgsql;

-- 3. Email verification
CREATE OR REPLACE FUNCTION verify_user_email(
    p_token_hash TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_token_record RECORD;
    v_user_id UUID;
BEGIN
    -- Token'ı kontrol et
    SELECT * INTO v_token_record
    FROM email_verification_tokens
    WHERE token_hash = p_token_hash
        AND is_used = false
        AND expires_at > NOW();

    -- Token bulunamadı veya geçersiz
    IF NOT FOUND THEN
        RETURN false;
    END IF;

    -- User'ı verify et
    UPDATE users
    SET email_verified = true,
        email_confirmed_at = NOW()
    WHERE id = v_token_record.user_id;

    -- Token'ı kullanılmış olarak işaretle
    UPDATE email_verification_tokens
    SET is_used = true,
        used_at = NOW()
    WHERE id = v_token_record.id;

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- 4. Password reset token doğrulama
CREATE OR REPLACE FUNCTION verify_password_reset_token(
    p_token_hash TEXT
)
RETURNS UUID AS $$
DECLARE
    v_token_record RECORD;
BEGIN
    -- Token'ı kontrol et
    SELECT * INTO v_token_record
    FROM password_reset_tokens
    WHERE token_hash = p_token_hash
        AND is_used = false
        AND expires_at > NOW();

    -- Token bulunamadı veya geçersiz
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    RETURN v_token_record.user_id;
END;
$$ LANGUAGE plpgsql;

-- 5. Password güncelleme ve token'ı kullanılmış işaretleme
CREATE OR REPLACE FUNCTION reset_user_password(
    p_token_hash TEXT,
    p_new_password_hash TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_token_record RECORD;
BEGIN
    -- Token'ı kontrol et
    SELECT * INTO v_token_record
    FROM password_reset_tokens
    WHERE token_hash = p_token_hash
        AND is_used = false
        AND expires_at > NOW();

    -- Token bulunamadı veya geçersiz
    IF NOT FOUND THEN
        RETURN false;
    END IF;

    -- Password'u güncelle
    UPDATE users
    SET password_hash = p_new_password_hash,
        updated_at = NOW()
    WHERE id = v_token_record.user_id;

    -- Token'ı kullanılmış olarak işaretle
    UPDATE password_reset_tokens
    SET is_used = true,
        used_at = NOW()
    WHERE id = v_token_record.id;

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- 6. User audit log kaydetme
CREATE OR REPLACE FUNCTION log_user_event(
    p_user_id UUID,
    p_event_type TEXT,
    p_event_description TEXT DEFAULT NULL,
    p_event_data JSONB DEFAULT '{}'::jsonb,
    p_client_ip INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_request_method TEXT DEFAULT NULL,
    p_request_path TEXT DEFAULT NULL,
    p_risk_level TEXT DEFAULT 'low',
    p_is_suspicious BOOLEAN DEFAULT false
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO user_audit_log (
        user_id,
        event_type,
        event_description,
        event_data,
        client_ip,
        user_agent,
        request_method,
        request_path,
        risk_level,
        is_suspicious
    ) VALUES (
        p_user_id,
        p_event_type,
        p_event_description,
        p_event_data,
        p_client_ip,
        p_user_agent,
        p_request_method,
        p_request_path,
        p_risk_level,
        p_is_suspicious
    )
    RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- 7. Son login zamanını güncelleme
CREATE OR REPLACE FUNCTION update_last_login(
    p_user_id UUID
)
RETURNS void AS $$
BEGIN
    UPDATE users
    SET last_login = NOW()
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- 8. Kullanıcının şüpheli aktivitelerini kontrol et
CREATE OR REPLACE FUNCTION check_suspicious_activity(
    p_user_id UUID,
    p_time_window INTERVAL DEFAULT '1 hour'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_failed_login_count INTEGER;
    v_suspicious_count INTEGER;
BEGIN
    -- Son 1 saat içinde başarısız login denemelerini say
    SELECT COUNT(*)
    INTO v_failed_login_count
    FROM user_audit_log
    WHERE user_id = p_user_id
        AND event_type = 'login_failed'
        AND created_at > (NOW() - p_time_window);

    -- Şüpheli aktivite sayısı
    SELECT COUNT(*)
    INTO v_suspicious_count
    FROM user_audit_log
    WHERE user_id = p_user_id
        AND is_suspicious = true
        AND created_at > (NOW() - p_time_window);

    -- 5'ten fazla başarısız giriş veya şüpheli aktivite varsa true dön
    IF v_failed_login_count > 5 OR v_suspicious_count > 3 THEN
        RETURN true;
    END IF;

    RETURN false;
END;
$$ LANGUAGE plpgsql;

-- 9. Kullanıcı istatistikleri
CREATE OR REPLACE FUNCTION get_user_stats(
    p_user_id UUID
)
RETURNS TABLE(
    total_logins BIGINT,
    last_login_date TIMESTAMP WITH TIME ZONE,
    total_password_resets BIGINT,
    account_age_days INTEGER,
    is_verified BOOLEAN,
    total_audit_events BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM user_audit_log WHERE user_id = p_user_id AND event_type = 'login_success') as total_logins,
        u.last_login as last_login_date,
        (SELECT COUNT(*) FROM password_reset_tokens WHERE user_id = p_user_id AND is_used = true) as total_password_resets,
        EXTRACT(DAY FROM (NOW() - u.created_at))::INTEGER as account_age_days,
        u.email_verified as is_verified,
        (SELECT COUNT(*) FROM user_audit_log WHERE user_id = p_user_id) as total_audit_events
    FROM users u
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- 10. Expired token'ları otomatik temizleme (kullanılmamış ve expired olanlar)
CREATE OR REPLACE FUNCTION auto_cleanup_tokens()
RETURNS TABLE(
    deleted_verification_tokens INTEGER,
    deleted_reset_tokens INTEGER
) AS $$
DECLARE
    v_verification_count INTEGER;
    v_reset_count INTEGER;
BEGIN
    -- Email verification tokens
    DELETE FROM email_verification_tokens
    WHERE expires_at < NOW() AND is_used = false;
    GET DIAGNOSTICS v_verification_count = ROW_COUNT;

    -- Password reset tokens
    DELETE FROM password_reset_tokens
    WHERE expires_at < NOW() AND is_used = false;
    GET DIAGNOSTICS v_reset_count = ROW_COUNT;

    RETURN QUERY SELECT v_verification_count, v_reset_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Helper Functions tamamlandı! 🎉
-- ============================================
