# MarkaMind Authentication Migration Plan
## PASETO to Supabase Auth + JWT Migration

---

## =� **M0GRASYON �ZETI**

**Hedef:** Mevcut karma_1k PASETO + Custom Auth sisteminden Supabase Auth + JWT sistemine ge�i_
**S�re:** 2-3 g�n
**Risk Seviyesi:** D�_�k
**Veri Kayb1:** Yok

---

## =
 **MEVCUT DURUMU ANAL0Z0**

### Mevcut Authentication Servisleri:
-  `app/services/auth_service.py` - Temel auth (KALACAK)
- L `app/services/enhanced_auth_service.py` - PASETO tabanl1 (S0L0NECEK)
- L `app/services/paseto_service.py` - PASETO token y�netimi (S0L0NECEK)
- L `app/services/dpop_service.py` - DPoP protokol� (S0L0NECEK)
- = `app/services/oauth_service.py` - OAuth servisi (G�NCELLENECEK)

### Mevcut Database Tablolar1:
**Supabase Auth ile Uyumlu (KALACAK):**
- `users` - Kullan1c1 bilgileri
- `password_reset_tokens` - ^ifre s1f1rlama
- `email_verification_tokens` - Email dorulama

**Kald1r1lacak Tablolar:**
- `user_sessions` - Custom session y�netimi (Supabase Auth halleder)
- `oauth_providers` - Custom OAuth (Supabase Auth halleder)

**0_ Mant11 Tablolar1 (KALACAK):**
- `brands`, `chatbots`, `conversations`, `feedback` - 0_ mant11
- `knowledge_base_entries`, `uploads` - Dosya y�netimi
- `api_keys` - API anahtarlar1
- `user_audit_log` - Audit log

---

## =� **S0L0NECEK DOSYALAR**

### 1. Servis Dosyalar
```bash
rm app/services/enhanced_auth_service.py
rm app/services/paseto_service.py
rm app/services/dpop_service.py
```

### 2. Test Dosyalar1
```bash
rm tests/test_step3.py  # PASETO testleri
rm tests/test_step6.py  # Enhanced auth testleri
```

### 3. Migration Dosyalar1
```bash
rm migrations/add_auth_columns.sql  # Custom auth i�in
```

### 4. Ge�ici Config Dosyalar1
```bash
rm .md/setup-fastapi.md  # Ge�ici setup dosyas1
```

---

## =� **DATABASE M0GRASYON SCRIPTLERI**

### 1. Gereksiz Tablolar1 Kald1r
```sql
-- Custom session tablosunu kald1r (Supabase Auth kullanaca1z)
DROP TABLE IF EXISTS user_sessions CASCADE;

-- Custom OAuth providers tablosunu kald1r (Supabase Auth kullanaca1z)
DROP TABLE IF EXISTS oauth_providers CASCADE;
```

### 2. Users Tablosunu Supabase Auth ile Uyumlu Hale Getir
```sql
-- Supabase Auth i�in gerekli alanlar1 ekle/g�ncelle
ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_hash text,
ADD COLUMN IF NOT EXISTS email_confirmed_at timestamp with time zone,
ADD COLUMN IF NOT EXISTS raw_app_meta_data jsonb DEFAULT '{}',
ADD COLUMN IF NOT EXISTS raw_user_meta_data jsonb DEFAULT '{}',
ADD COLUMN IF NOT EXISTS aud text DEFAULT 'authenticated',
ADD COLUMN IF NOT EXISTS confirmation_token text,
ADD COLUMN IF NOT EXISTS recovery_token text,
ADD COLUMN IF NOT EXISTS phone text,
ADD COLUMN IF NOT EXISTS phone_confirmed_at timestamp with time zone;

-- Mevcut verileri Supabase uyumlu hale getir
UPDATE users SET
  email_confirmed_at = CASE WHEN email_verified = true THEN created_at ELSE NULL END,
  aud = 'authenticated'
WHERE email_confirmed_at IS NULL;

-- Gereksiz custom auth alanlar1n1 kald1r (eer varsa)
ALTER TABLE users DROP COLUMN IF EXISTS auth_method;
ALTER TABLE users DROP COLUMN IF EXISTS oauth_provider;
ALTER TABLE users DROP COLUMN IF EXISTS oauth_provider_id;
```

### 3. Indices ve Constraints G�ncellemesi
```sql
-- Supabase Auth i�in gerekli indexler
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_confirmation_token ON users(confirmation_token);
CREATE INDEX IF NOT EXISTS idx_users_recovery_token ON users(recovery_token);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_select_policy ON users
FOR SELECT USING (auth.uid() = id);

CREATE POLICY users_update_policy ON users
FOR UPDATE USING (auth.uid() = id);
```

---

## =' **KOD DE0^0KL0KLER0**

### 1. requirements.txt G�ncellemeleri
```txt
# Kald1r1lacak
- pyseto==1.7.2
- pynacl==1.5.0
- authlib==1.2.1
- httpx-oauth==0.13.0
- slowapi==0.1.9
- redis==4.5.4

# Eklenecek
+ PyJWT==2.8.0
```

### 2. app/config.py G�ncellemeleri
```python
# Kald1r1lacak konfig�rasyonlar:
- paseto_private_key
- paseto_symmetric_key
- oauth_google_client_id
- oauth_google_client_secret
- oauth_github_client_id
- oauth_github_client_secret
- redis_host, redis_port, redis_db
```

### 3. app/routers/auth.py B�y�k Revizyon
**Kald1r1lacak Endpoint'ler:**
- `/oauth/authorize` - Supabase Auth halleder
- `/oauth/login` - Supabase Auth halleder
- `/oauth/providers` - Supabase Auth halleder
- `/dpop/nonce` - DPoP kald1r1ld1

**G�ncellenecek Endpoint'ler:**
- `/register` - Supabase Auth kullanacak
- `/login` - Supabase Auth kullanacak
- `/refresh` - Supabase Auth token refresh
- `/logout` - Supabase Auth signOut




---

## =� **0MPLEMENTASYON ADIMLARI**

### Faz 1: Temizlik (30 dakika)
1. **Dosya Silme:**
   ```bash
   rm app/services/enhanced_auth_service.py
   rm app/services/paseto_service.py
   rm app/services/dpop_service.py
   rm tests/test_step3.py
   rm tests/test_step6.py
   ```

2. **Requirements G�ncellemesi:**
   ```bash
   pip uninstall pyseto pynacl authlib httpx-oauth slowapi redis
   pip install PyJWT==2.8.0
   ```

### Faz 2: Database Migration (15 dakika)
```bash
# PostgreSQL migration scriptlerini �al1_t1r
psql -d your_database -f migration_cleanup.sql
```

### Faz 3: Code Refactoring (2 saat)
1. **auth.py Router G�ncellemesi**
2. **dependencies.py JWT Implementation**
3. **config.py Temizlik**
4. **Import G�ncellemeleri**

### Faz 4: Test & Validation (30 dakika)
1. **Temel Auth Flow Testi**
2. **Avatar Upload Testi**
3. **Profile Update Testi**

---

## =� **YEN0 SUPABASE AUTH IMPLEMENTATION**

### Basit Login Example:
```python
from supabase import create_client, Client

supabase: Client = create_client(supabase_url, supabase_key)

# Login
async def login(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

### JWT Token Verification:
```python
import jwt
from app.config import settings

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## � **R0SK ANAL0Z0 VE �NLEMLER0**

### D�_�k Riskler:
1. **Avatar Upload:** Etkilenmez (ayr1 servis)
2. **0_ Mant11:** Brands, Chatbots vs. etkilenmez
3. **Database 0li_kileri:** Foreign key'ler korunur

### Potansiyel Sorunlar ve ��z�mleri:
1. **Session Kayb1:** Kullan1c1lar tekrar giri_ yapmak zorunda (Normal)
2. **OAuth Balant1lar1:** Supabase Dashboard'dan yeniden kurulmal1
3. **Rate Limiting:** Supabase Auth'un kendi rate limiting'i kullan1lacak

---

## <� **MIGRATION CHECKLIST**

### �n Haz1rl1k:
- [ ] Supabase Dashboard'da Authentication ayarlar1n1 yap1land1r
- [ ] Email Provider ayarlar1n1 yap (SMTP)
- [ ] OAuth Providers'lar1 Supabase'de tan1mla

### Database Migration:
- [ ] Custom tablolar silinecek (`user_sessions`, `oauth_providers`)
- [ ] `users` tablosu Supabase uyumlu hale getirilecek
- [ ] RLS policies eklendi

### Code Migration:
- [ ] PASETO servisleri silindi
- [ ] JWT implementation eklendi
- [ ] Router endpoint'leri g�ncellendi
- [ ] Dependencies JWT kullanmaya g�ncelleye

### Test & Validation:
- [ ] Login/Register �al1_1yor
- [ ] Token refresh �al1_1yor
- [ ] Avatar upload �al1_1yor
- [ ] Profile update �al1_1yor
- [ ] Logout �al1_1yor

---

## =� **PERFORMANS KAR^ILA^TIRMASI**

| Metrik | PASETO (�nce) | Supabase Auth (Sonra) |
|--------|---------------|----------------------|
| Kod Sat1r1 | ~2000 sat1r | ~500 sat1r |
| Servis Dosyas1 | 4 dosya | 1 dosya |
| External Dependency | 6 k�t�phane | 2 k�t�phane |
| G�venlik | Manuel | Otomatik |
| Bak1m | Y�ksek | D�_�k |
| Email Features | Manuel | Otomatik |

---

## = **SONU�**

Bu migration plan1 ile:
-  **%75 daha az kod**
-  **Otomatik g�venlik �nlemleri**
-  **Email verification haz1r**
-  **OAuth providers haz1r**
-  **S1f1r bak1m maliyeti**

**Tahmini S�re:** 3-4 saat
**Risk Seviyesi:** D�_�k
**Performans:** Art1_ bekleniyor