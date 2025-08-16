# MarkaMind - Markanıza Özel Yapay Zekâ Destekli Chatbox Sistemi

## 🎯 Proje Özeti

MarkaMind, markaların dijital iletişim gücünü artırmak üzere geliştirilmiş, tamamen özelleştirilebilir yapay zekâ tabanlı bir chatbox oluşturma platformudur. Bu platform sayesinde her marka, kendine özgü bir dijital asistan yaratabilir; hem görünümünü hem de konuşma tarzını kendi değerleri doğrultusunda şekillendirebilir.

## 🚀 Nasıl Çalışır?

### 1. Markanı Tanıt
Kullanıcı olarak sisteme giriş yaptıktan sonra markanıza dair temel bilgileri girerek süreci başlatırsınız.

### 2. Chatbox'ınızı Tasarlayın
Marka kimliğinizi yansıtan bir chatbox oluşturmanız için platform size geniş özelleştirme seçenekleri sunar:
- Renk düzenini belirleme
- Logo, görsel ve videolar ekleme
- Mesaj balonu renkleri ve stilleri
- Hazır animasyonlardan seçim yapma

### 3. Marka Bilgilerinizi Yükleyin
Markanızı anlatan metin, döküman veya içerikleri chatbox'a yüklersiniz. Yapay zekâ motoru, bu verileri analiz ederek sadece sizin markanıza özel cevaplar üretecek şekilde eğitilir.

### 4. Kodu Al, Web Sitene Ekle
Chatbox hazır olduktan sonra sistem size otomatik olarak bir adet entegre script sunar. Bu script, MarkaMind API'si ile bağlantı kurar ve widget formatındaki chatbox'ı:
- İster İKAS mağazanıza
- İster kendi özel web sitenize
kolayca entegre etmenizi sağlar.

## 🎯 Ne Sağlar?
- Marka ile tamamen uyumlu bir dijital iletişim aracı
- Tek panelden kolay yönetim ve özelleştirme
- Kod bilmeden dakikalar içinde yayınlanabilir widget
- Yapay zekâ ile güçlendirilmiş müşteri etkileşimi
- E-ticaret sitelerinde dönüşüm artırıcı akıllı destek

## 🧠 Backend Teknoloji Stack

- **Framework:** FastAPI
- **Veritabanı:** Supabase PostgreSQL
- **Kimlik Doğrulama:** Supabase Auth
- **Dosya Depolama:** Supabase Storage
- **AI/LLM:** OpenAI / Cohere / Mistral
- **Vector Search:** Pinecone (opsiyonel)
- **Background Tasks:** Celery veya FastAPI BackgroundTasks

## 📊 Veritabanı Tabloları

### 1. users - Kullanıcılar
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Supabase auth üzerinden gelen kullanıcı kimliği |
| email | TEXT | Kullanıcının e-posta adresi |
| full_name | TEXT | Ad ve soyad |
| role | TEXT | "admin", "user" vb. (opsiyonel) |
| created_at | TIMESTAMP | Kayıt tarihi |

### 2. brands - Markalar
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Marka kimliği |
| user_id | UUID (FK) | Sahibi olan kullanıcı (users.id) |
| name | TEXT | Marka adı |
| slug | TEXT | URL uyumlu kısa ad (eşsiz) |
| description | TEXT | Marka hakkında bilgi |
| logo_url | TEXT | Supabase Storage URL |
| theme_color | TEXT | Marka rengi (#hex) |
| is_active | BOOLEAN | Pasif/aktif marka |
| created_at | TIMESTAMP | Oluşturulma tarihi |

### 3. chatbots - Chatbotlar
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Chatbot kimliği |
| brand_id | UUID (FK) | Bağlı marka (brands.id) |
| name | TEXT | Chatbot adı |
| avatar_url | TEXT | Botun avatar görseli |
| primary_color | TEXT | Ana renk (hex) |
| secondary_color | TEXT | İkincil renk |
| animation_style | TEXT | Seçilen animasyon tipi |
| script_token | TEXT (unique) | Widget'a özel public token (iframe erişimi) |
| language | TEXT | "tr", "en", "de" vb. |
| status | TEXT | "draft", "published", "archived" |
| created_at | TIMESTAMP | Oluşturulma tarihi |

### 4. knowledge_base_entries - Bilgi Kaynakları
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Kayıt kimliği |
| chatbot_id | UUID (FK) | Bağlı olduğu chatbot |
| source_type | TEXT | "manual", "pdf", "url", "txt" |
| source_url | TEXT | Dosya linki (pdf, video vb.) |
| content | TEXT | Ham içerik metni |
| embedding_id | TEXT | Embedding vektör ID (vespa, pinecone vs.) |
| token_count | INTEGER | İçeriğin token uzunluğu |
| status | TEXT | "processing", "ready", "failed" |
| created_at | TIMESTAMP | Oluşturulma tarihi |

### 5. chat_prompts - Sistem Prompts / Ayarlar
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Ayar kaydı kimliği |
| chatbot_id | UUID (FK) | Hangi bota ait |
| prompt_text | TEXT | Sistem mesajı ("sen bir destek asistanısın..." gibi) |
| temperature | FLOAT | Modelin yaratıcılığı (0.0 - 1.0) |
| context_size | INTEGER | Kaç tokena kadar içerik alacağı |
| top_p | FLOAT | Sampling kontrolü |
| created_at | TIMESTAMP | Oluşturulma tarihi |

### 6. conversations - Konuşma Oturumları
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Satır kimliği |
| chatbot_id | UUID (FK) | Chatbot referansı |
| session_id | TEXT | Oturumu tanımlayan benzersiz kimlik |
| user_input | TEXT | Kullanıcının yazdığı mesaj |
| bot_response | TEXT | Chatbot'un yanıtı |
| source_entry_id | UUID (FK) | Hangi içerikten bilgi geldi (opsiyonel) |
| latency_ms | INTEGER | Yanıt süresi (milisaniye) |
| created_at | TIMESTAMP | Mesajın tarihi |

### 7. feedback - Kullanıcı Geri Bildirimleri
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Geri bildirim kimliği |
| conversation_id | UUID (FK) | Bağlantılı konuşma satırı |
| rating | INTEGER | 1-5 arası puan |
| comment | TEXT | Opsiyonel açıklama |
| created_at | TIMESTAMP | Oluşturulma zamanı |

### 8. uploads - Dosya Takibi
| Alan Adı | Tip | Açıklama |
|----------|-----|----------|
| id | UUID (PK) | Yükleme kimliği |
| chatbot_id | UUID (FK) | Bağlı bot |
| file_name | TEXT | Dosya adı |
| file_type | TEXT | pdf / image / video / txt |
| storage_url | TEXT | Supabase Storage URL |
| processed | BOOLEAN | İşlenmiş mi? |
| created_at | TIMESTAMP | Oluşturulma zamanı |

## 🔗 İlişkisel Veritabanı Şeması (ERD)

```
users
  └── brands (user_id)
       └── chatbots (brand_id)
             ├── knowledge_base_entries (chatbot_id)
             ├── chat_prompts (chatbot_id)
             ├── conversations (chatbot_id)
             │     └── feedback (conversation_id)
             └── uploads (chatbot_id)
```

## 📡 API Endpoint'leri

### 🧑‍💼 Kullanıcı & Kimlik Doğrulama (Auth)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/me` | Giriş yapan kullanıcının profil bilgilerini getirir | 🔒 |
| PUT | `/me` | Kullanıcı bilgilerini günceller | 🔒 |

### 🏷️ Marka Yönetimi (brands)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/brands/` | Kullanıcının tüm markalarını listeler | 🔒 |
| POST | `/brands/` | Yeni bir marka oluşturur | 🔒 |
| GET | `/brands/{brand_id}` | Belirli bir markayı getirir | 🔒 |
| PUT | `/brands/{brand_id}` | Marka bilgilerini günceller | 🔒 |
| DELETE | `/brands/{brand_id}` | Markayı siler (soft delete olabilir) | 🔒 |

### 🤖 Chatbot Yönetimi (chatbots)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/chatbots/` | Kullanıcının tüm chatbotlarını listeler | 🔒 |
| POST | `/chatbots/` | Yeni bir chatbot oluşturur | 🔒 |
| GET | `/chatbots/{chatbot_id}` | Belirli bir chatbot bilgisi | 🔒 |
| PUT | `/chatbots/{chatbot_id}` | Chatbot ayarlarını günceller | 🔒 |
| DELETE | `/chatbots/{chatbot_id}` | Chatbot'u siler | 🔒 |

### ⚙️ Chatbot Ayarları (chat_prompts)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/chatbots/{chatbot_id}/prompt` | Chatbot sistem promptunu getirir | 🔒 |
| POST | `/chatbots/{chatbot_id}/prompt` | Yeni prompt oluşturur / günceller | 🔒 |

### 📚 Bilgi Girişi & Eğitim İçeriği (knowledge_base_entries)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/chatbots/{chatbot_id}/knowledge` | Botun tüm bilgi kaynaklarını listeler | 🔒 |
| POST | `/chatbots/{chatbot_id}/knowledge` | Yeni içerik yükler (manuel metin, dosya vs.) | 🔒 |
| GET | `/knowledge/{entry_id}` | Belirli bir bilgi girişini getirir | 🔒 |
| DELETE | `/knowledge/{entry_id}` | İçeriği siler | 🔒 |

### 🗂️ Dosya Yükleme (uploads)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| POST | `/uploads/` | Supabase Storage'a dosya yükler (signed URL ile) | 🔒 |
| GET | `/uploads/{upload_id}` | Yüklenmiş dosya detayını getirir | 🔒 |

### 💬 Mesajlaşma & Chat API (conversations)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| POST | `/chat/{script_token}` | Chat widget'ından gelen mesajı işler ve cevap üretir | 🆓 |
| GET | `/chatbots/{chatbot_id}/conversations` | Kullanıcının botuna ait konuşmaları listeler | 🔒 |
| GET | `/conversations/{conversation_id}` | Tekil konuşma detaylarını getirir | 🔒 |

### ⭐ Geri Bildirim (feedback)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| POST | `/feedback/` | Kullanıcı mesaj/cevap için puan verir | 🆓 |
| GET | `/chatbots/{chatbot_id}/feedback` | Botun aldığı geri bildirimleri listeler | 🔒 |

### 🧩 Widget & Script
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/widget/{script_token}` | Script token üzerinden iframe bot kodunu döner | 🆓 |
| GET | `/widget/{script_token}/meta` | Widget'a ait konfigürasyon bilgileri döner | 🆓 |

### 🔒 Admin / Sistemsel (isteğe bağlı)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| GET | `/admin/users` | Tüm kullanıcıları listeler (super admin) | 🔒 |
| GET | `/admin/metrics` | Bot kullanımı, performans logları vb. | 🔒 |

### 🧠 RAG Eğitim & Embedding API (opsiyonel advanced)
| Metot | Endpoint | Açıklama | Yetki |
|-------|----------|----------|-------|
| POST | `/embed/process/{entry_id}` | Bilgi girişini embed vector'e dönüştür | 🔒 |
| POST | `/embed/batch/{chatbot_id}` | Botun tüm içeriklerini batch embed eder | 🔒 |
| POST | `/search/{chatbot_id}` | Kullanıcının mesajını semantik aramayla eşleştirir | 🔒 |

## 🧱 Backend Yol Haritası

### 1. Proje Temel Yapılandırması
- FastAPI projesini başlat (uvicorn, fastapi, pydantic)
- Sanal ortam oluştur ve bağımlılıkları yükle (poetry veya pip)
- main.py, routers/, services/, models/, schemas/, utils/ gibi klasör yapısını oluştur
- Ortam değişkenlerini dotenv ile yönet

### 2. Supabase Auth Entegrasyonu
- Supabase projesi oluştur
- Supabase JWT doğrulama mekanizmasını backend ile entegre et
- Login / signup işlemlerini frontend'e bırak, FastAPI içinde kullanıcı kimliğini Authorization Bearer üzerinden kontrol et
- Supabase Auth ile birlikte gelen user_id ile tüm verileri ilişkilendir

### 3. Veritabanı Modelleme (Supabase PostgreSQL)
- Yukarıda belirtilen temel tabloları oluştur

### 4. Dosya Yükleme & İçerik Yönetimi (Supabase Storage)
- Supabase Storage bucket oluştur (chatbot-files vb.)
- PDF, görsel, video yükleme için presigned URL üret
- Yüklenen verileri Supabase'de sakla ve veritabanına linkle
- İçeriklerin analiz edilmesi için background task (RAG eğitimi) kuyruğa alınsın

### 5. Chatbot Eğitimi & Mesajlama API'si
- Chatbot'a ait içerikler üzerinden knowledge_base oluştur
- Bu içeriklere semantic search uygulamak için OpenAI / Cohere / Mistral gibi embed servisleri entegrasyonu (opsiyonel Pinecone)
- /chat endpoint'i oluştur: POST /chat: Kullanıcının mesajını alır → chatbot verisi + semantic search → yanıt üretir
- chatbot_id, session_id ile geçmiş konuşmalar saklanır (opsiyonel cache ile hız)

### 6. Script & Widget API'si
- Her chatbox'a özel script_token oluştur (UUID)
- GET /widget/{script_token}: Iframe olarak çağrıldığında chatbox embed kodunu döner
- Chat mesaj API'si CORS izinleriyle iframe'de kullanılabilir olmalı
- Gerekirse iframe üzerinden public data'lar JWT imzası ile korunur

### 7. Admin Panel (Opsiyonel)
- FastAPI ile basit bir admin arayüzü (ya da direkt Supabase Studio ile kontrol)
- Kullanıcı aktiviteleri, hatalı istekler, bot kullanımları loglanır

### 8. Background İşlemler ve Görevler
- RAG eğitimi ve embed işlemleri için Celery veya BackgroundTasks entegrasyonu
- Yüksek hacimli isteklerde iş kuyruklama ve zamanlamalar (PDF analizleri vb.)

### 9. Güvenlik & Rate Limiting
- JWT doğrulama katmanı
- Token expiration ve refresh sistemi
- IP bazlı rate limit (örn: slowapi, fastapi-limiter)
- CORS yönetimi (allow_origins, allow_credentials)

### 10. Test & API Dokümantasyonu
- Pytest ile unit test altyapısı
- FastAPI Swagger UI üzerinden test edilebilir uçlar
- Postman collection oluşturulabilir

## 📝 Notlar

- 🔒 işareti yetkili kullanıcı girişi gerektiren endpointtir (JWT kontrolü yapılır)
- 🆓 işareti herkese açık (public) endpointtir (örnek: widget görüntüleme)
- RESTful kurallarına uygun şekilde organize edilmiştir
- Next.js frontend'e kolayca entegre edilir
- iframe script tarafı ayrı tutulur
- Kapsamlı ve genişleyebilir modülerlik sunar