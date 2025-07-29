# MarkaMind API Endpoint'leri - Detaylı Dokümantasyon

## 1. Kullanıcı Yönetimi (Authentication & Authorization)

### POST /api/auth/register
**Açıklama:** Yeni kullanıcı kaydı oluşturur
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Example Corp",
  "phone": "+90 555 123 4567"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Kullanıcı başarıyla oluşturuldu",
  "data": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "verification_required": true
  }
}
```
**Error (400):**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Email zaten kullanımda"
}
```

### POST /api/auth/login
**Açıklama:** Kullanıcı giriş işlemi ve JWT token oluşturma
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt-token-here",
    "refresh_token": "refresh-token-here",
    "expires_in": 3600,
    "user": {
      "id": "uuid-here",
      "email": "user@example.com",
      "first_name": "John",
      "subscription_plan": "basic"
    }
  }
}
```

### POST /api/auth/logout
**Açıklama:** Kullanıcı çıkış işlemi ve token invalidation
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "message": "Başarıyla çıkış yapıldı"
}
```

### GET /api/auth/me
**Açıklama:** Mevcut kullanıcının profil bilgilerini getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Example Corp",
    "phone": "+90 555 123 4567",
    "subscription_plan": "professional",
    "created_at": "2024-01-15T10:30:00Z",
    "email_verified": true
  }
}
```

### PUT /api/auth/profile
**Açıklama:** Kullanıcı profil bilgilerini günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "company_name": "New Company",
  "phone": "+90 555 999 8888"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Profil başarıyla güncellendi",
  "data": {
    "updated_fields": ["first_name", "company_name"]
  }
}
```

### POST /api/auth/forgot-password
**Açıklama:** Şifre sıfırlama talebi oluşturur ve email gönderir
**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Şifre sıfırlama linki email adresinize gönderildi"
}
```

### POST /api/auth/reset-password
**Açıklama:** Token ile şifre sıfırlama işlemi
**Request Body:**
```json
{
  "token": "reset-token-here",
  "new_password": "newSecurePassword123"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Şifre başarıyla güncellendi"
}
```

## 2. Chatbot Yönetimi

### GET /api/chatbots
**Açıklama:** Kullanıcının tüm chatbot'larını sayfalama ile listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `page` (int): Sayfa numarası (default: 1)
- `limit` (int): Sayfa başına kayıt (default: 10, max: 50)
- `search` (string): Chatbot adında arama
- `status` (string): active, inactive, training
**Response (200):**
```json
{
  "success": true,
  "data": {
    "chatbots": [
      {
        "id": "chatbot-uuid",
        "name": "Müşteri Destek Botu",
        "description": "7/24 müşteri destek chatbotu",
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "last_trained": "2024-01-20T14:20:00Z",
        "message_count": 1250,
        "integration_status": "embedded"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 25,
      "items_per_page": 10
    }
  }
}
```

### POST /api/chatbots
**Açıklama:** Yeni chatbot oluşturur
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Yeni Chatbot",
  "description": "Açıklama",
  "category": "customer_support",
  "language": "tr",
  "initial_message": "Merhaba! Size nasıl yardımcı olabilirim?",
  "fallback_message": "Üzgünüm, bu konuda yardımcı olamıyorum."
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Chatbot başarıyla oluşturuldu",
  "data": {
    "chatbot_id": "new-chatbot-uuid",
    "name": "Yeni Chatbot",
    "status": "draft",
    "created_at": "2024-01-21T15:30:00Z"
  }
}
```

### GET /api/chatbots/{chatbot_id}
**Açıklama:** Belirli bir chatbot'un detaylı bilgilerini getirir
**Headers:** `Authorization: Bearer {token}`
**Path Parameters:**
- `chatbot_id` (string): Chatbot UUID'si
**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "chatbot-uuid",
    "name": "Müşteri Destek Botu",
    "description": "7/24 müşteri destek chatbotu",
    "category": "customer_support",
    "language": "tr",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:20:00Z",
    "last_trained": "2024-01-20T14:20:00Z",
    "training_data_count": 150,
    "message_count": 1250,
    "average_response_time": 1.2,
    "satisfaction_score": 4.6,
    "settings": {
      "initial_message": "Merhaba! Size nasıl yardımcı olabilirim?",
      "fallback_message": "Üzgünüm, bu konuda yardımcı olamıyorum.",
      "max_response_length": 500,
      "temperature": 0.7
    },
    "appearance": {
      "theme": "modern",
      "primary_color": "#007bff",
      "avatar_url": "https://example.com/avatar.png"
    }
  }
}
```

### PUT /api/chatbots/{chatbot_id}
**Açıklama:** Chatbot bilgilerini güncelle
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Güncellenmiş Chatbot Adı",
  "description": "Yeni açıklama",
  "settings": {
    "initial_message": "Yeni karşılama mesajı",
    "fallback_message": "Yeni fallback mesajı",
    "temperature": 0.8
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Chatbot başarıyla güncellendi",
  "data": {
    "updated_fields": ["name", "description", "settings"],
    "last_updated": "2024-01-21T16:45:00Z"
  }
}
```

### DELETE /api/chatbots/{chatbot_id}
**Açıklama:** Chatbot'u kalıcı olarak siler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `confirm` (boolean): Silme onayı (required: true)
**Response (200):**
```json
{
  "success": true,
  "message": "Chatbot başarıyla silindi"
}
```

### POST /api/chatbots/{chatbot_id}/duplicate
**Açıklama:** Mevcut chatbot'u kopyalar
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "new_name": "Kopya - Müşteri Destek Botu",
  "copy_training_data": true,
  "copy_appearance": true,
  "copy_settings": true
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Chatbot başarıyla kopyalandı",
  "data": {
    "new_chatbot_id": "duplicated-chatbot-uuid",
    "name": "Kopya - Müşteri Destek Botu"
  }
}
```

## 3. Veri Eğitimi ve İçerik Yönetimi

### POST /api/chatbots/{chatbot_id}/train/pdf
**Açıklama:** PDF dosyası ile chatbot eğitimi
**Headers:** `Authorization: Bearer {token}`, `Content-Type: multipart/form-data`
**Form Data:**
- `file` (file): PDF dosyası (max: 50MB)
- `extract_images` (boolean): Görsel içerik çıkarımı
- `chunk_size` (int): Metin parça boyutu (default: 1000)
**Response (202):**
```json
{
  "success": true,
  "message": "PDF işleme başlatıldı",
  "data": {
    "job_id": "training-job-uuid",
    "estimated_completion": "2024-01-21T17:15:00Z",
    "file_info": {
      "filename": "training_data.pdf",
      "size": 2048576,
      "pages": 45
    }
  }
}
```

### POST /api/chatbots/{chatbot_id}/train/text
**Açıklama:** Metin dosyası ile chatbot eğitimi
**Headers:** `Authorization: Bearer {token}`, `Content-Type: multipart/form-data`
**Form Data:**
- `file` (file): Metin dosyası (.txt, .docx, .md)
- `encoding` (string): Dosya kodlaması (default: utf-8)
**Response (202):**
```json
{
  "success": true,
  "message": "Metin dosyası işleme başlatıldı",
  "data": {
    "job_id": "training-job-uuid",
    "estimated_completion": "2024-01-21T17:10:00Z"
  }
}
```

### POST /api/chatbots/{chatbot_id}/train/url
**Açıklama:** Web URL'sinden veri çekerek eğitim
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "urls": [
    "https://example.com/faq",
    "https://example.com/about"
  ],
  "max_depth": 2,
  "follow_external_links": false,
  "extract_images": false
}
```
**Response (202):**
```json
{
  "success": true,
  "message": "URL tarama başlatıldı",
  "data": {
    "job_id": "training-job-uuid",
    "urls_count": 2,
    "estimated_completion": "2024-01-21T17:20:00Z"
  }
}
```

### POST /api/chatbots/{chatbot_id}/train/manual
**Açıklama:** Manuel metin girişi ile eğitim
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "training_data": [
    {
      "question": "Çalışma saatleriniz nedir?",
      "answer": "Hafta içi 09:00-18:00 arası hizmet veriyoruz."
    },
    {
      "question": "İade politikanız nasıl?",
      "answer": "14 gün içinde iade yapabilirsiniz."
    }
  ],
  "category": "faq"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Manuel eğitim verisi eklendi",
  "data": {
    "added_count": 2,
    "job_id": "training-job-uuid"
  }
}
```

### GET /api/chatbots/{chatbot_id}/training-data
**Açıklama:** Chatbot'un eğitim verilerini listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `page` (int): Sayfa numarası
- `limit` (int): Sayfa başına kayıt
- `type` (string): pdf, text, url, manual
- `search` (string): İçerik araması
**Response (200):**
```json
{
  "success": true,
  "data": {
    "training_data": [
      {
        "id": "data-uuid",
        "type": "pdf",
        "filename": "product_manual.pdf",
        "content_preview": "Bu kılavuz ürün kullanımı hakkında...",
        "chunk_count": 25,
        "created_at": "2024-01-20T14:30:00Z",
        "status": "processed"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 48
    },
    "summary": {
      "total_chunks": 245,
      "types": {
        "pdf": 15,
        "text": 10,
        "url": 8,
        "manual": 15
      }
    }
  }
}
```

### DELETE /api/chatbots/{chatbot_id}/training-data/{data_id}
**Açıklama:** Belirli eğitim verisini siler
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "message": "Eğitim verisi silindi",
  "data": {
    "deleted_chunks": 25,
    "retrain_required": true
  }
}
```

### POST /api/chatbots/{chatbot_id}/retrain
**Açıklama:** Chatbot'u mevcut verilerle yeniden eğitir
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "include_data_types": ["pdf", "text", "manual"],
  "training_parameters": {
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```
**Response (202):**
```json
{
  "success": true,
  "message": "Yeniden eğitim başlatıldı",
  "data": {
    "job_id": "retrain-job-uuid",
    "estimated_completion": "2024-01-21T18:00:00Z",
    "data_count": 245
  }
}
```

### GET /api/chatbots/{chatbot_id}/training-status
**Açıklama:** Eğitim işleminin durumunu kontrol eder
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `job_id` (string): Takip edilecek iş ID'si
**Response (200):**
```json
{
  "success": true,
  "data": {
    "job_id": "training-job-uuid",
    "status": "processing",
    "progress": 65,
    "current_step": "Metin işleme",
    "estimated_completion": "2024-01-21T17:45:00Z",
    "processed_items": 32,
    "total_items": 50,
    "errors": []
  }
}
```

### POST /api/chatbots/{chatbot_id}/rag/embed
**Açıklama:** Eğitim verisini RAG sistemi için vektörleştirir ve embedding'leri oluşturur
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "data_ids": ["data-uuid-1", "data-uuid-2"],
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "embedding_model": "text-embedding-ada-002"
}
```
**Response (202):**
```json
{
  "success": true,
  "message": "Embedding işlemi başlatıldı",
  "data": {
    "job_id": "embedding-job-uuid",
    "estimated_completion": "2024-01-21T18:15:00Z",
    "data_count": 2,
    "estimated_chunks": 450
  }
}
```

### GET /api/chatbots/{chatbot_id}/rag/embeddings
**Açıklama:** Chatbot'un RAG embedding'lerini listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `page` (int): Sayfa numarası
- `limit` (int): Sayfa başına kayıt
- `search` (string): İçerik araması
- `data_source` (string): pdf, text, url, manual
**Response (200):**
```json
{
  "success": true,
  "data": {
    "embeddings": [
      {
        "id": "embedding-uuid",
        "chunk_id": "chunk-uuid",
        "content_preview": "Bu kılavuz ürün kullanımı hakkında...",
        "source_type": "pdf",
        "source_id": "data-uuid",
        "vector_dimension": 1536,
        "created_at": "2024-01-21T16:30:00Z",
        "metadata": {
          "page_number": 5,
          "chunk_index": 12,
          "similarity_threshold": 0.8
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 25,
      "total_embeddings": 2450
    },
    "summary": {
      "total_chunks": 2450,
      "total_vectors": 2450,
      "embedding_model": "text-embedding-ada-002",
      "vector_dimension": 1536
    }
  }
}
```

### POST /api/chatbots/{chatbot_id}/rag/search
**Açıklama:** RAG sistemi ile semantik arama yapar
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "query": "Ürün iade politikası nedir?",
  "top_k": 5,
  "similarity_threshold": 0.7,
  "include_metadata": true,
  "filter": {
    "source_type": ["pdf", "manual"],
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z"
    }
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "query": "Ürün iade politikası nedir?",
    "results": [
      {
        "chunk_id": "chunk-uuid-1",
        "content": "Ürün iade politikamız 14 gün içinde koşulsuz iade imkanı sunmaktadır...",
        "similarity_score": 0.95,
        "source": {
          "type": "pdf",
          "filename": "iade_politikasi.pdf",
          "page": 3
        },
        "metadata": {
          "created_at": "2024-01-20T14:30:00Z",
          "chunk_index": 8
        }
      },
      {
        "chunk_id": "chunk-uuid-2",
        "content": "İade işlemleri için müşteri hizmetleri ile iletişime geçebilirsiniz...",
        "similarity_score": 0.87,
        "source": {
          "type": "manual",
          "category": "customer_service"
        },
        "metadata": {
          "created_at": "2024-01-19T10:15:00Z",
          "chunk_index": 15
        }
      }
    ],
    "total_results": 2,
    "search_time_ms": 45,
    "embedding_time_ms": 12
  }
}
```

### DELETE /api/chatbots/{chatbot_id}/rag/embeddings/{embedding_id}
**Açıklama:** Belirli bir embedding'i siler
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "message": "Embedding başarıyla silindi",
  "data": {
    "embedding_id": "embedding-uuid",
    "chunk_id": "chunk-uuid",
    "deleted_at": "2024-01-21T17:30:00Z"
  }
}
```

### POST /api/chatbots/{chatbot_id}/rag/optimize
**Açıklama:** RAG vektör veritabanını optimize eder
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "operation": "rebuild_index",
  "similarity_threshold": 0.8,
  "remove_duplicates": true,
  "merge_similar_chunks": true
}
```
**Response (202):**
```json
{
  "success": true,
  "message": "RAG optimizasyonu başlatıldı",
  "data": {
    "job_id": "optimization-job-uuid",
    "estimated_completion": "2024-01-21T19:00:00Z",
    "current_embeddings": 2450,
    "estimated_after_optimization": 2100
  }
}
```

### GET /api/chatbots/{chatbot_id}/rag/stats
**Açıklama:** RAG sistemi istatistiklerini getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_embeddings": 2450,
    "total_chunks": 2450,
    "vector_dimension": 1536,
    "embedding_model": "text-embedding-ada-002",
    "index_size_mb": 15.6,
    "average_chunk_size": 850,
    "sources": {
      "pdf": 1200,
      "text": 800,
      "url": 300,
      "manual": 150
    },
    "performance": {
      "average_search_time_ms": 45,
      "average_embedding_time_ms": 12,
      "index_build_time": "2024-01-21T16:45:00Z"
    },
    "quality_metrics": {
      "duplicate_chunks": 25,
      "low_quality_chunks": 12,
      "coverage_percentage": 95.8
    }
  }
}
```

## 4. Chatbot Özelleştirme

### PUT /api/chatbots/{chatbot_id}/appearance
**Açıklama:** Chatbot'un görsel özelleştirmelerini günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "theme": "modern",
  "primary_color": "#007bff",
  "secondary_color": "#6c757d",
  "background_color": "#ffffff",
  "text_color": "#333333",
  "border_radius": 8,
  "font_family": "Inter",
  "avatar": {
    "type": "image",
    "url": "https://example.com/avatar.png"
  },
  "chat_bubble": {
    "user_color": "#007bff",
    "bot_color": "#f8f9fa",
    "shadow": true
  },
  "position": {
    "side": "right",
    "bottom_margin": 20,
    "side_margin": 20
  },
  "header": {
    "show": true,
    "title": "Müşteri Destek",
    "subtitle": "Online • Genellikle 2dk içinde yanıtlar"
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Görsel ayarlar güncellendi",
  "data": {
    "preview_url": "https://api.markamind.com/preview/chatbot-uuid"
  }
}
```

### PUT /api/chatbots/{chatbot_id}/behavior
**Açıklama:** Chatbot'un davranışsal ayarlarını günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "personality": {
    "tone": "friendly",
    "formality": "informal",
    "emoji_usage": true
  },
  "response_settings": {
    "max_length": 500,
    "temperature": 0.7,
    "response_delay": 1000
  },
  "conversation_flow": {
    "initial_message": "Merhaba! Size nasıl yardımcı olabilirim? 😊",
    "fallback_message": "Üzgünüm, bu konuda size yardımcı olamıyorum. Başka bir şey deneyebilir misiniz?",
    "goodbye_message": "Yardımcı olabildiysem ne mutlu! İyi günler! 👋"
  },
  "auto_responses": {
    "greeting_detection": true,
    "goodbye_detection": true,
    "thanks_detection": true
  },
  "escalation": {
    "enabled": true,
    "trigger_keywords": ["insan", "temsilci", "şikayet"],
    "escalation_message": "Sizi bir temsilcimize bağlıyorum..."
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Davranış ayarları güncellendi"
}
```

### GET /api/animations
**Açıklama:** Mevcut animasyon kütüphanesini listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `category` (string): entrance, typing, button, transition
- `subscription_level` (string): basic, professional
**Response (200):**
```json
{
  "success": true,
  "data": {
    "animations": [
      {
        "id": "slide-in-right",
        "name": "Sağdan Kaydırma",
        "category": "entrance",
        "preview_url": "https://animations.markamind.com/slide-in-right.gif",
        "subscription_required": "basic",
        "duration": 300
      },
      {
        "id": "bounce-in",
        "name": "Zıplama Girişi",
        "category": "entrance",
        "preview_url": "https://animations.markamind.com/bounce-in.gif",
        "subscription_required": "professional",
        "duration": 600
      }
    ],
    "categories": {
      "entrance": 15,
      "typing": 8,
      "button": 12,
      "transition": 10
    }
  }
}
```

### PUT /api/chatbots/{chatbot_id}/animation
**Açıklama:** Chatbot animasyonunu seçer/değiştirir
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "entrance_animation": "slide-in-right",
  "typing_animation": "dots-bounce",
  "button_animation": "pulse",
  "transition_animation": "fade",
  "animation_speed": "normal"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Animasyonlar güncellendi",
  "data": {
    "preview_url": "https://api.markamind.com/preview/chatbot-uuid"
  }
}
```

### GET /api/chatbots/{chatbot_id}/preview
**Açıklama:** Chatbot'un canlı önizlemesini oluşturur
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `device` (string): desktop, mobile, tablet
- `theme` (string): light, dark
**Response (200):**
```json
{
  "success": true,
  "data": {
    "preview_url": "https://preview.markamind.com/chatbot-uuid?token=preview-token",
    "expires_at": "2024-01-21T19:00:00Z",
    "embed_code": "<iframe src='...' width='400' height='600'></iframe>"
  }
}
```

## 5. Entegrasyon

### GET /api/chatbots/{chatbot_id}/embed-code
**Açıklama:** Iframe embed kodu oluşturur
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `width` (string): Genişlik (default: "400px")
- `height` (string): Yükseklik (default: "600px")
- `position` (string): fixed, inline
**Response (200):**
```json
{
  "success": true,
  "data": {
    "embed_code": "<iframe src='https://embed.markamind.com/chatbot-uuid' width='400' height='600' frameborder='0' style='border-radius: 8px;'></iframe>",
    "preview_url": "https://embed.markamind.com/chatbot-uuid",
    "customization_options": {
      "width": "400px",
      "height": "600px",
      "border_radius": "8px",
      "shadow": true
    }
  }
}
```

### GET /api/chatbots/{chatbot_id}/script-code
**Açıklama:** JavaScript widget script kodu oluşturur
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `position` (string): bottom-right, bottom-left, top-right, top-left
- `trigger` (string): auto, click, scroll
**Response (200):**
```json
{
  "success": true,
  "data": {
    "script_code": "<script>\n(function(d, s, id) {\n  var js, fjs = d.getElementsByTagName(s)[0];\n  if (d.getElementById(id)) return;\n  js = d.createElement(s); js.id = id;\n  js.src = 'https://widget.markamind.com/chatbot-uuid.js';\n  fjs.parentNode.insertBefore(js, fjs);\n}(document, 'script', 'markamind-chatbot'));\n</script>",
    "widget_url": "https://widget.markamind.com/chatbot-uuid.js",
    "integration_guide": "https://docs.markamind.com/integration/widget"
  }
}
```

### POST /api/chatbots/{chatbot_id}/test-integration
**Açıklama:** Entegrasyon testini gerçekleştirir
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "test_url": "https://example.com/test-page",
  "integration_type": "script",
  "test_scenarios": [
    "widget_load",
    "message_send",
    "response_receive"
  ]
}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "test_id": "test-uuid",
    "status": "completed",
    "results": {
      "widget_load": {
        "success": true,
        "load_time": 1.2,
        "message": "Widget başarıyla yüklendi"
      },
      "message_send": {
        "success": true,
        "response_time": 850,
        "message": "Mesaj gönderimi başarılı"
      },
      "response_receive": {
        "success": true,
        "response_quality": 0.95,
        "message": "Yanıt başarıyla alındı"
      }
    },
    "overall_score": 98,
    "recommendations": []
  }
}
```

## 6. Sohbet İşlemleri

### POST /api/chat/{chatbot_id}/message
**Açıklama:** Chatbot'a mesaj gönderir ve yanıt alır
**Headers:** `Content-Type: application/json`
**Request Body:**
```json
{
  "message": "Merhaba, çalışma saatleriniz nedir?",
  "session_id": "session-uuid",
  "user_id": "user-uuid",
  "context": {
    "page_url": "https://example.com/contact",
    "user_agent": "Mozilla/5.0...",
    "timestamp": "2024-01-21T15:30:00Z"
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "data": {
    "message_id": "message-uuid",
    "response": "Merhaba! Hafta içi 09:00-18:00 arası hizmet veriyoruz. Size başka nasıl yardımcı olabilirim?",
    "response_time": 1.2,
    "confidence": 0.95,
    "sources": [
      {
        "type": "training_data",
        "id": "data-uuid",
        "relevance": 0.98
      }
    ],
    "suggested_actions": [
      {
        "type": "quick_reply",
        "text": "İletişim bilgileri",
        "action": "contact_info"
      }
    ]
  }
}
```

### GET /api/chat/{chatbot_id}/history
**Açıklama:** Sohbet geçmişini getirir
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `session_id` (string): Belirli oturum geçmişi
- `user_id` (string): Belirli kullanıcı geçmişi
- `start_date` (string): Başlangıç tarihi (ISO 8601)
- `end_date` (string): Bitiş tarihi (ISO 8601)
- `page` (int): Sayfa numarası
- `limit` (int): Kayıt sayısı
**Response (200):**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "session_id": "session-uuid",
        "user_id": "user-uuid",
        "started_at": "2024-01-21T15:30:00Z",
        "ended_at": "2024-01-21T15:45:00Z",
        "message_count": 8,
        "satisfaction_score": 4.5,
        "messages": [
          {
            "id": "msg-uuid",
            "type": "user",
            "content": "Merhaba",
            "timestamp": "2024-01-21T15:30:00Z"
          },
          {
            "id": "msg-uuid-2",
            "type": "bot",
            "content": "Merhaba! Size nasıl yardımcı olabilirim?",
            "timestamp": "2024-01-21T15:30:02Z",
            "response_time": 1.1
          }
        ]
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_conversations": 95
    },
    "summary": {
      "total_messages": 1250,
      "average_session_duration": 8.5,
      "average_satisfaction": 4.3
    }
  }
}
```

### DELETE /api/chat/{chatbot_id}/history
**Açıklama:** Sohbet geçmişini temizler
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "scope": "all",
  "before_date": "2024-01-01T00:00:00Z",
  "session_ids": ["session-uuid-1", "session-uuid-2"]
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Sohbet geçmişi temizlendi",
  "data": {
    "deleted_conversations": 45,
    "deleted_messages": 380
  }
}
```

### GET /api/chat/{chatbot_id}/active-sessions
**Açıklama:** Aktif sohbet oturumlarını listeler
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "active_sessions": [
      {
        "session_id": "session-uuid",
        "user_id": "user-uuid",
        "started_at": "2024-01-21T15:30:00Z",
        "last_activity": "2024-01-21T15:35:00Z",
        "message_count": 5,
        "status": "active",
        "user_info": {
          "location": "Istanbul, TR",
          "device": "desktop",
          "page": "https://example.com/contact"
        }
      }
    ],
    "total_active": 12,
    "peak_concurrent": 25
  }
}
```

## 7. Sanal Mağaza Yönetimi

### GET /api/virtual-store
**Açıklama:** Kullanıcının sanal mağaza bilgilerini getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "store_id": "store-uuid",
    "name": "Örnek Mağaza",
    "description": "Sanal test mağazası",
    "theme": "modern",
    "logo_url": "https://example.com/logo.png",
    "settings": {
      "currency": "TRY",
      "language": "tr",
      "tax_rate": 0.18,
      "shipping_enabled": true
    },
    "stats": {
      "total_products": 25,
      "total_chatbots": 8,
      "test_sessions": 142
    },
    "created_at": "2024-01-15T10:00:00Z",
    "status": "active"
  }
}
```

### PUT /api/virtual-store/settings
**Açıklama:** Sanal mağaza ayarlarını günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Yeni Mağaza Adı",
  "description": "Güncellenmiş açıklama",
  "theme": "minimal",
  "settings": {
    "currency": "EUR",
    "language": "en",
    "tax_rate": 0.20,
    "shipping_enabled": false
  },
  "branding": {
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "logo_url": "https://example.com/new-logo.png"
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Mağaza ayarları güncellendi",
  "data": {
    "updated_fields": ["name", "theme", "settings", "branding"]
  }
}
```

### GET /api/virtual-store/products
**Açıklama:** Mağaza ürünlerini listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `page` (int): Sayfa numarası
- `limit` (int): Sayfa başına ürün
- `category` (string): Ürün kategorisi
- `search` (string): Ürün adında arama
- `has_chatbot` (boolean): Chatbot atanmış ürünler
**Response (200):**
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "id": "product-uuid",
        "name": "Akıllı Telefon Pro",
        "description": "Son teknoloji akıllı telefon",
        "price": 15999.99,
        "currency": "TRY",
        "category": "electronics",
        "image_url": "https://example.com/phone.jpg",
        "stock": 50,
        "sku": "PHONE-PRO-001",
        "chatbot": {
          "assigned": true,
          "chatbot_id": "chatbot-uuid",
          "chatbot_name": "Telefon Uzmanı"
        },
        "created_at": "2024-01-20T14:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_products": 25
    },
    "categories": [
      {"name": "electronics", "count": 10},
      {"name": "clothing", "count": 8},
      {"name": "books", "count": 7}
    ]
  }
}
```

### POST /api/virtual-store/products
**Açıklama:** Yeni ürün ekler
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Yeni Ürün",
  "description": "Ürün açıklaması",
  "price": 299.99,
  "currency": "TRY",
  "category": "electronics",
  "sku": "PROD-001",
  "stock": 100,
  "images": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg"
  ],
  "specifications": {
    "color": "Siyah",
    "weight": "200g",
    "dimensions": "15x8x1cm"
  },
  "tags": ["yeni", "popüler", "indirim"]
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Ürün başarıyla eklendi",
  "data": {
    "product_id": "new-product-uuid",
    "name": "Yeni Ürün",
    "sku": "PROD-001"
  }
}
```

### PUT /api/virtual-store/products/{product_id}
**Açıklama:** Ürün bilgilerini günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Güncellenmiş Ürün Adı",
  "description": "Yeni açıklama",
  "price": 349.99,
  "stock": 75,
  "specifications": {
    "color": "Beyaz",
    "weight": "180g"
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Ürün başarıyla güncellendi",
  "data": {
    "updated_fields": ["name", "description", "price", "stock", "specifications"]
  }
}
```

### DELETE /api/virtual-store/products/{product_id}
**Açıklama:** Ürünü siler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `force` (boolean): Chatbot atamalı ürünü zorla sil
**Response (200):**
```json
{
  "success": true,
  "message": "Ürün başarıyla silindi",
  "data": {
    "chatbot_assignments_removed": 1
  }
}
```

### POST /api/virtual-store/products/{product_id}/assign-chatbot
**Açıklama:** Ürüne chatbot atar
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "chatbot_id": "chatbot-uuid",
  "priority": 1,
  "custom_greeting": "Bu ürün hakkında size nasıl yardımcı olabilirim?",
  "context_info": {
    "product_focus": true,
    "include_specifications": true,
    "include_reviews": false
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Chatbot başarıyla atandı",
  "data": {
    "assignment_id": "assignment-uuid",
    "chatbot_name": "Ürün Uzmanı",
    "preview_url": "https://store.markamind.com/product-uuid/chat"
  }
}
```

### GET /api/virtual-store/products/{product_id}/chatbot
**Açıklama:** Ürün chatbot bilgilerini getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "assignment_id": "assignment-uuid",
    "chatbot": {
      "id": "chatbot-uuid",
      "name": "Ürün Uzmanı",
      "status": "active"
    },
    "custom_greeting": "Bu ürün hakkında size nasıl yardımcı olabilirim?",
    "context_info": {
      "product_focus": true,
      "include_specifications": true,
      "include_reviews": false
    },
    "stats": {
      "total_conversations": 45,
      "average_satisfaction": 4.7,
      "conversion_rate": 0.23
    },
    "assigned_at": "2024-01-20T16:00:00Z"
  }
}
```

### POST /api/virtual-store/test-scenario
**Açıklama:** Alışveriş senaryosu testi başlatır
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "scenario_type": "product_inquiry",
  "products": ["product-uuid-1", "product-uuid-2"],
  "test_cases": [
    {
      "name": "Ürün bilgisi sorma",
      "messages": [
        "Bu telefonun özellikleri nedir?",
        "Fiyatı ne kadar?",
        "Stokta var mı?"
      ]
    },
    {
      "name": "Karşılaştırma",
      "messages": [
        "İki telefon arasındaki fark nedir?",
        "Hangisini önerirsiniz?"
      ]
    }
  ]
}
```
**Response (202):**
```json
{
  "success": true,
  "message": "Test senaryosu başlatıldı",
  "data": {
    "test_id": "test-scenario-uuid",
    "estimated_completion": "2024-01-21T16:15:00Z",
    "test_cases_count": 2,
    "products_count": 2
  }
}
```

## 8. Paket ve Abonelik Yönetimi

### GET /api/packages
**Açıklama:** Mevcut paketleri ve özelliklerini listeler
**Query Parameters:**
- `active_only` (boolean): Sadece aktif paketler
- `compare_with` (string): Mevcut paket ile karşılaştırma
**Response (200):**
```json
{
  "success": true,
  "data": {
    "packages": [
      {
        "id": "basic",
        "name": "Temel Paket",
        "description": "Başlangıç seviyesi için ideal",
        "price": {
          "monthly": 99,
          "yearly": 990,
          "currency": "TRY"
        },
        "features": {
          "chatbot_count": 3,
          "monthly_messages": 1000,
          "training_data_mb": 50,
          "integrations": ["iframe", "script"],
          "animations": 10,
          "analytics": "basic",
          "support": "email"
        },
        "limits": {
          "api_calls_per_day": 1000,
          "concurrent_users": 50,
          "data_retention_days": 30
        }
      },
      {
        "id": "professional",
        "name": "Profesyonel Paket",
        "description": "Büyük işletmeler için",
        "price": {
          "monthly": 299,
          "yearly": 2990,
          "currency": "TRY"
        },
        "features": {
          "chatbot_count": 10,
          "monthly_messages": 10000,
          "training_data_mb": 500,
          "integrations": ["iframe", "script", "api", "webhook"],
          "animations": 50,
          "analytics": "advanced",
          "support": "priority",
          "virtual_store": true,
          "white_label": true
        },
        "limits": {
          "api_calls_per_day": 10000,
          "concurrent_users": 500,
          "data_retention_days": 365
        }
      }
    ],
    "current_package": "basic",
    "billing_cycle": "monthly"
  }
}
```

### GET /api/user/subscription
**Açıklama:** Kullanıcının mevcut abonelik detaylarını getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "subscription_id": "sub-uuid",
    "package": {
      "id": "professional",
      "name": "Profesyonel Paket"
    },
    "status": "active",
    "billing_cycle": "monthly",
    "current_period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-02-01T00:00:00Z"
    },
    "next_billing_date": "2024-02-01T00:00:00Z",
    "amount": 299,
    "currency": "TRY",
    "usage": {
      "chatbots_used": 7,
      "chatbots_limit": 10,
      "messages_used": 6450,
      "messages_limit": 10000,
      "data_used_mb": 245,
      "data_limit_mb": 500
    },
    "payment_method": {
      "type": "card",
      "last_four": "1234",
      "expiry": "12/26"
    },
    "auto_renewal": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### POST /api/subscription/upgrade
**Açıklama:** Paket yükseltme işlemi
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "target_package": "professional",
  "billing_cycle": "yearly",
  "proration": true,
  "effective_date": "immediate"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Paket başarıyla yükseltildi",
  "data": {
    "new_package": "professional",
    "effective_date": "2024-01-21T16:00:00Z",
    "prorated_charge": 200,
    "next_billing_date": "2024-02-21T16:00:00Z",
    "invoice_id": "inv-uuid"
  }
}
```

### POST /api/subscription/downgrade
**Açıklama:** Paket düşürme işlemi
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "target_package": "basic",
  "effective_date": "next_billing_cycle",
  "reason": "cost_optimization"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Paket düşürme planlandı",
  "data": {
    "current_package": "professional",
    "target_package": "basic",
    "effective_date": "2024-02-01T00:00:00Z",
    "credit_amount": 0,
    "limitations_notice": [
      "Chatbot sayısı 10'dan 3'e düşecek",
      "Aylık mesaj limiti 10,000'den 1,000'e düşecek"
    ]
  }
}
```

### POST /api/subscription/cancel
**Açıklama:** Aboneliği iptal eder
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "cancellation_type": "end_of_period",
  "reason": "not_using_enough",
  "feedback": "Özellikler ihtiyacımdan fazlaydı"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Abonelik iptal edildi",
  "data": {
    "cancellation_date": "2024-01-21T16:30:00Z",
    "service_end_date": "2024-02-01T00:00:00Z",
    "refund_amount": 0,
    "data_retention_until": "2024-02-15T00:00:00Z"
  }
}
```

### GET /api/subscription/usage
**Açıklama:** Detaylı paket kullanım istatistikleri
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): current, last_month, last_3_months
- `breakdown` (boolean): Günlük detay
**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-02-01T00:00:00Z",
      "current": true
    },
    "usage": {
      "chatbots": {
        "used": 7,
        "limit": 10,
        "percentage": 70
      },
      "messages": {
        "used": 6450,
        "limit": 10000,
        "percentage": 64.5,
        "daily_average": 207
      },
      "training_data": {
        "used_mb": 245,
        "limit_mb": 500,
        "percentage": 49
      },
      "api_calls": {
        "used": 45670,
        "limit": 310000,
        "percentage": 14.7
      }
    },
    "trends": {
      "messages_growth": "+15%",
      "peak_usage_day": "2024-01-18",
      "most_active_chatbot": "chatbot-uuid"
    },
    "daily_breakdown": [
      {
        "date": "2024-01-20",
        "messages": 234,
        "api_calls": 1567,
        "peak_concurrent": 12
      }
    ]
  }
}
```

### GET /api/subscription/limits
**Açıklama:** Mevcut paket limitlerini ve kalan kotaları getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "package": "professional",
    "limits": {
      "chatbots": {
        "limit": 10,
        "used": 7,
        "remaining": 3,
        "status": "ok"
      },
      "monthly_messages": {
        "limit": 10000,
        "used": 6450,
        "remaining": 3550,
        "status": "ok",
        "projected_usage": 8200
      },
      "training_data_mb": {
        "limit": 500,
        "used": 245,
        "remaining": 255,
        "status": "ok"
      },
      "daily_api_calls": {
        "limit": 10000,
        "used": 1567,
        "remaining": 8433,
        "status": "ok",
        "resets_at": "2024-01-22T00:00:00Z"
      }
    },
    "warnings": [],
    "recommendations": [
      "Mesaj kullanımınız normal seviyelerde, şu anki paket yeterli"
    ]
  }
}
```

## 9. Analiz ve Raporlama

### GET /api/analytics/{chatbot_id}/overview
**Açıklama:** Chatbot genel performans özeti
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): today, week, month, quarter, year, custom
- `start_date` (string): Özel dönem başlangıcı
- `end_date` (string): Özel dönem bitişi
- `timezone` (string): Zaman dilimi (default: Europe/Istanbul)
**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z",
      "label": "Ocak 2024"
    },
    "summary": {
      "total_conversations": 1250,
      "total_messages": 8750,
      "unique_users": 856,
      "average_session_duration": 8.5,
      "satisfaction_score": 4.3,
      "resolution_rate": 0.87
    },
    "trends": {
      "conversations_change": "+23%",
      "messages_change": "+18%",
      "satisfaction_change": "+0.2",
      "users_change": "+31%"
    },
    "top_metrics": {
      "busiest_day": {
        "date": "2024-01-15",
        "conversations": 89
      },
      "peak_hour": "14:00-15:00",
      "most_common_query": "çalışma saatleri",
      "fastest_response": 0.8
    },
    "performance": {
      "uptime": 99.8,
      "average_response_time": 1.2,
      "error_rate": 0.02,
      "cache_hit_rate": 0.85
    }
  }
}
```

### GET /api/analytics/{chatbot_id}/conversations
**Açıklama:** Detaylı sohbet analizi
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): Analiz dönemi
- `group_by` (string): day, hour, week
- `include_sentiment` (boolean): Duygu analizi dahil et
**Response (200):**
```json
{
  "success": true,
  "data": {
    "conversation_stats": {
      "total": 1250,
      "completed": 1087,
      "abandoned": 163,
      "escalated": 45,
      "completion_rate": 0.87
    },
    "message_analysis": {
      "total_messages": 8750,
      "user_messages": 4375,
      "bot_messages": 4375,
      "average_per_conversation": 7.0
    },
    "duration_analysis": {
      "average_seconds": 510,
      "median_seconds": 420,
      "distribution": {
        "0-2min": 25,
        "2-5min": 45,
        "5-10min": 20,
        "10min+": 10
      }
    },
    "topic_analysis": {
      "top_topics": [
        {
          "topic": "çalışma saatleri",
          "count": 234,
          "percentage": 18.7
        },
        {
          "topic": "ürün bilgisi",
          "count": 189,
          "percentage": 15.1
        }
      ]
    },
    "sentiment_analysis": {
      "positive": 0.65,
      "neutral": 0.28,
      "negative": 0.07,
      "trends": {
        "positive_trend": "+5%",
        "negative_reasons": ["slow response", "wrong answer"]
      }
    },
    "timeline": [
      {
        "date": "2024-01-01",
        "conversations": 42,
        "completion_rate": 0.85,
        "average_duration": 480
      }
    ]
  }
}
```

### GET /api/analytics/{chatbot_id}/user-satisfaction
**Açıklama:** Kullanıcı memnuniyet skorları ve feedback analizi
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): Analiz dönemi
- `include_comments` (boolean): Yorum analizini dahil et
**Response (200):**
```json
{
  "success": true,
  "data": {
    "overall_satisfaction": {
      "average_score": 4.3,
      "total_ratings": 756,
      "response_rate": 0.61,
      "score_distribution": {
        "5": 45,
        "4": 32,
        "3": 15,
        "2": 5,
        "1": 3
      }
    },
    "satisfaction_trends": [
      {
        "date": "2024-01-01",
        "average_score": 4.1,
        "rating_count": 23
      }
    ],
    "feedback_analysis": {
      "positive_keywords": [
        {"word": "hızlı", "count": 89},
        {"word": "yardımcı", "count": 76},
        {"word": "kolay", "count": 45}
      ],
      "negative_keywords": [
        {"word": "yavaş", "count": 12},
        {"word": "anlamadı", "count": 8}
      ]
    },
    "improvement_areas": [
      {
        "area": "Response Speed",
        "score": 3.8,
        "priority": "high",
        "suggestion": "Optimize response time for better user experience"
      }
    ],
    "nps_score": {
      "score": 67,
      "promoters": 0.72,
      "passives": 0.23,
      "detractors": 0.05
    }
  }
}
```

### GET /api/analytics/{chatbot_id}/performance-metrics
**Açıklama:** Detaylı teknik performans metrikleri
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): Analiz dönemi
- `metrics` (array): İstenen metrik türleri
**Response (200):**
```json
{
  "success": true,
  "data": {
    "response_time": {
      "average": 1.2,
      "median": 1.0,
      "p95": 2.1,
      "p99": 3.5,
      "timeline": [
        {
          "timestamp": "2024-01-21T14:00:00Z",
          "average": 1.1,
          "requests": 45
        }
      ]
    },
    "accuracy_metrics": {
      "intent_recognition": 0.94,
      "answer_relevance": 0.89,
      "confidence_distribution": {
        "high": 0.75,
        "medium": 0.20,
        "low": 0.05
      }
    },
    "system_metrics": {
      "uptime": 99.8,
      "error_rate": 0.02,
      "timeout_rate": 0.01,
      "cache_hit_rate": 0.85
    },
    "resource_usage": {
      "cpu_average": 45,
      "memory_average": 512,
      "storage_used": 2048,
      "bandwidth_gb": 15.6
    },
    "quality_scores": {
      "answer_quality": 4.2,
      "conversation_flow": 4.0,
      "user_engagement": 3.8
    }
  }
}
```

### GET /api/analytics/{chatbot_id}/popular-questions
**Açıklama:** Sık sorulan sorular ve trend analizi
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): Analiz dönemi
- `limit` (int): Sonuç sayısı limiti
- `category` (string): Soru kategorisi filtresi
**Response (200):**
```json
{
  "success": true,
  "data": {
    "top_questions": [
      {
        "question": "Çalışma saatleriniz nedir?",
        "count": 234,
        "percentage": 18.7,
        "category": "info",
        "avg_confidence": 0.96,
        "trend": "+15%",
        "successful_answers": 0.98
      },
      {
        "question": "İade nasıl yapabilirim?",
        "count": 189,
        "percentage": 15.1,
        "category": "support",
        "avg_confidence": 0.91,
        "trend": "+8%",
        "successful_answers": 0.87
      }
    ],
    "question_categories": [
      {
        "category": "info",
        "count": 456,
        "percentage": 36.5,
        "avg_satisfaction": 4.5
      },
      {
        "category": "support",
        "count": 321,
        "percentage": 25.7,
        "avg_satisfaction": 4.1
      }
    ],
    "unanswered_questions": [
      {
        "question": "Özel indirimlriniz var mı?",
        "count": 12,
        "last_asked": "2024-01-21T15:30:00Z",
        "priority": "high"
      }
    ],
    "trending_topics": [
      {
        "topic": "Kargo durumu",
        "growth": "+45%",
        "period": "last_week"
      }
    ]
  }
}
```

### GET /api/analytics/{chatbot_id}/response-times
**Açıklama:** Yanıt süresi detaylı istatistikleri
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): Analiz dönemi
- `breakdown` (string): hourly, daily, weekly
**Response (200):**
```json
{
  "success": true,
  "data": {
    "overall_stats": {
      "average_ms": 1200,
      "median_ms": 1000,
      "min_ms": 250,
      "max_ms": 5000,
      "std_deviation": 450
    },
    "percentiles": {
      "p50": 1000,
      "p75": 1400,
      "p90": 2000,
      "p95": 2500,
      "p99": 4000
    },
    "time_breakdown": [
      {
        "period": "2024-01-21T14:00:00Z",
        "average_ms": 1150,
        "request_count": 45,
        "slowest_query": "karmaşık ürün karşılaştırması"
      }
    ],
    "performance_by_query_type": [
      {
        "type": "simple_faq",
        "average_ms": 800,
        "count": 567,
        "percentage": 45.4
      },
      {
        "type": "complex_search",
        "average_ms": 2100,
        "count": 123,
        "percentage": 9.8
      }
    ],
    "peak_hours": [
      {
        "hour": "14:00-15:00",
        "average_ms": 1450,
        "request_count": 89
      }
    ],
    "improvement_suggestions": [
      "Cache frequently asked questions",
      "Optimize complex query processing"
    ]
  }
}
```

### GET /api/analytics/compare
**Açıklama:** Çoklu chatbot performans karşılaştırması
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `chatbot_ids` (array): Karşılaştırılacak chatbot ID'leri
- `metrics` (array): Karşılaştırılacak metrikler
- `period` (string): Karşılaştırma dönemi
**Response (200):**
```json
{
  "success": true,
  "data": {
    "comparison_period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z"
    },
    "chatbots": [
      {
        "id": "chatbot-1",
        "name": "Müşteri Destek",
        "metrics": {
          "conversations": 1250,
          "satisfaction": 4.3,
          "response_time": 1.2,
          "resolution_rate": 0.87
        }
      },
      {
        "id": "chatbot-2",
        "name": "Satış Danışmanı",
        "metrics": {
          "conversations": 856,
          "satisfaction": 4.1,
          "response_time": 1.5,
          "resolution_rate": 0.82
        }
      }
    ],
    "best_performers": {
      "conversations": "chatbot-1",
      "satisfaction": "chatbot-1",
      "response_time": "chatbot-1",
      "resolution_rate": "chatbot-1"
    },
    "trends": {
      "chatbot-1": {
        "conversations_growth": "+23%",
        "satisfaction_trend": "+0.2"
      },
      "chatbot-2": {
        "conversations_growth": "+12%",
        "satisfaction_trend": "-0.1"
      }
    },
    "recommendations": [
      {
        "chatbot_id": "chatbot-2",
        "area": "response_time",
        "suggestion": "Optimize training data for faster responses"
      }
    ]
  }
}
```

### POST /api/analytics/{chatbot_id}/export
**Açıklama:** Analiz raporunu farklı formatlarda dışa aktarır
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "format": "pdf",
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "sections": [
    "overview",
    "conversations",
    "satisfaction",
    "performance"
  ],
  "include_charts": true,
  "language": "tr"
}
```
**Response (202):**
```json
{
  "success": true,
  "message": "Rapor oluşturma başlatıldı",
  "data": {
    "export_id": "export-uuid",
    "estimated_completion": "2024-01-21T16:45:00Z",
    "format": "pdf",
    "sections_count": 4
  }
}
```

**Export Status Check - GET /api/analytics/export/{export_id}/status:**
```json
{
  "success": true,
  "data": {
    "export_id": "export-uuid",
    "status": "completed",
    "progress": 100,
    "download_url": "https://reports.markamind.com/export-uuid.pdf",
    "expires_at": "2024-01-28T16:45:00Z",
    "file_size": 2048576
  }
}
```

## 10. Yönetim ve Ayarlar

### GET /api/settings/notification
**Açıklama:** Kullanıcının bildirim ayarlarını getirir
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "email_notifications": {
      "enabled": true,
      "types": {
        "training_completed": true,
        "high_error_rate": true,
        "monthly_report": true,
        "billing_reminder": true,
        "security_alerts": true
      },
      "frequency": "immediate"
    },
    "sms_notifications": {
      "enabled": false,
      "phone": "+90555123456",
      "types": {
        "critical_alerts": false,
        "system_downtime": false
      }
    },
    "webhook_notifications": {
      "enabled": true,
      "webhook_url": "https://example.com/webhooks/markamind",
      "events": [
        "message_received",
        "conversation_ended",
        "satisfaction_rated"
      ]
    },
    "in_app_notifications": {
      "enabled": true,
      "types": {
        "new_messages": true,
        "system_updates": true,
        "feature_announcements": true
      }
    }
  }
}
```

### PUT /api/settings/notification
**Açıklama:** Bildirim ayarlarını günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "email_notifications": {
    "enabled": true,
    "types": {
      "training_completed": true,
      "high_error_rate": false,
      "monthly_report": true
    },
    "frequency": "daily_digest"
  },
  "webhook_notifications": {
    "enabled": true,
    "webhook_url": "https://newexample.com/webhooks",
    "events": ["message_received", "conversation_ended"]
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Bildirim ayarları güncellendi",
  "data": {
    "updated_settings": ["email_notifications", "webhook_notifications"],
    "webhook_verified": true
  }
}
```

### GET /api/settings/api-keys
**Açıklama:** Kullanıcının API anahtarlarını listeler
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "data": {
    "api_keys": [
      {
        "id": "key-uuid",
        "name": "Production API Key",
        "key_preview": "mm_...8f2a",
        "permissions": ["read", "write", "admin"],
        "last_used": "2024-01-21T15:30:00Z",
        "created_at": "2024-01-15T10:00:00Z",
        "expires_at": null,
        "status": "active",
        "usage_stats": {
          "requests_today": 245,
          "requests_month": 7890
        }
      }
    ],
    "usage_limits": {
      "max_keys": 5,
      "current_count": 2,
      "rate_limit_per_key": 1000
    }
  }
}
```

### POST /api/settings/api-keys
**Açıklama:** Yeni API anahtarı oluşturur
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Development API Key",
  "permissions": ["read", "write"],
  "expires_at": "2024-12-31T23:59:59Z",
  "rate_limit": 500,
  "allowed_ips": ["192.168.1.100", "10.0.0.5"],
  "description": "Development environment için API anahtarı"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "API anahtarı oluşturuldu",
  "data": {
    "api_key_id": "new-key-uuid",
    "name": "Development API Key",
    "api_key": "mm_1234567890abcdef1234567890abcdef",
    "permissions": ["read", "write"],
    "expires_at": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-21T16:00:00Z"
  },
  "warning": "Bu API anahtarını güvenli bir yerde saklayın. Bir daha gösterilmeyecektir."
}
```

### DELETE /api/settings/api-keys/{key_id}
**Açıklama:** API anahtarını siler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `confirm` (boolean): Silme onayı
**Response (200):**
```json
{
  "success": true,
  "message": "API anahtarı başarıyla silindi",
  "data": {
    "revoked_at": "2024-01-21T16:30:00Z",
    "last_usage": "2024-01-21T15:45:00Z"
  }
}
```

### GET /api/logs/{chatbot_id}
**Açıklama:** Chatbot'un sistem loglarını getirir
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `level` (string): debug, info, warning, error
- `start_date` (string): Log başlangıç tarihi
- `end_date` (string): Log bitiş tarihi
- `limit` (int): Kayıt sayısı limiti
- `search` (string): Log içeriği araması
**Response (200):**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "log-uuid",
        "timestamp": "2024-01-21T16:30:15.123Z",
        "level": "info",
        "message": "Message processed successfully",
        "context": {
          "user_id": "user-uuid",
          "session_id": "session-uuid",
          "response_time": 1.2,
          "confidence": 0.95
        },
        "metadata": {
          "request_id": "req-uuid",
          "ip_address": "192.168.1.100"
        }
      },
      {
        "id": "log-uuid-2",
        "timestamp": "2024-01-21T16:25:30.456Z",
        "level": "warning",
        "message": "Low confidence response",
        "context": {
          "confidence": 0.45,
          "fallback_used": true,
          "user_message": "çok karmaşık soru"
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 15,
      "total_logs": 1450
    },
    "summary": {
      "total_logs": 1450,
      "by_level": {
        "debug": 823,
        "info": 567,
        "warning": 45,
        "error": 15
      },
      "error_rate": 0.01
    }
  }
}
```

### GET /api/system/health
**Açıklama:** Sistem durumu ve sağlık kontrolü
**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-21T16:35:00Z",
    "version": "1.2.3",
    "uptime": 2592000,
    "services": {
      "api": {
        "status": "healthy",
        "response_time": 45,
        "last_check": "2024-01-21T16:34:00Z"
      },
      "database": {
        "status": "healthy",
        "connections": 25,
        "max_connections": 100,
        "last_check": "2024-01-21T16:34:30Z"
      },
      "ai_service": {
        "status": "healthy",
        "queue_size": 3,
        "processing_time": 1.2,
        "last_check": "2024-01-21T16:35:00Z"
      },
      "storage": {
        "status": "healthy",
        "used_space_gb": 150,
        "total_space_gb": 1000,
        "last_check": "2024-01-21T16:34:45Z"
      }
    },
    "metrics": {
      "requests_per_minute": 450,
      "average_response_time": 1.1,
      "error_rate": 0.02,
      "cache_hit_rate": 0.87
    }
  }
}
```

## 11. Dosya Yönetimi

### POST /api/files/upload
**Açıklama:** Dosya yükleme işlemi (PDF, resim, doküman)
**Headers:** `Authorization: Bearer {token}`, `Content-Type: multipart/form-data`
**Form Data:**
- `file` (file): Yüklenecek dosya
- `category` (string): avatar, training_data, logo, document
- `description` (string): Dosya açıklaması
- `public` (boolean): Herkese açık dosya mı
**Response (201):**
```json
{
  "success": true,
  "message": "Dosya başarıyla yüklendi",
  "data": {
    "file_id": "file-uuid",
    "filename": "document.pdf",
    "original_filename": "eğitim_verisi.pdf",
    "size": 2048576,
    "mime_type": "application/pdf",
    "category": "training_data",
    "url": "https://files.markamind.com/file-uuid",
    "thumbnail_url": "https://files.markamind.com/file-uuid/thumb",
    "upload_date": "2024-01-21T16:40:00Z",
    "metadata": {
      "pages": 45,
      "text_extracted": true,
      "language": "tr"
    }
  }
}
```

### GET /api/files/{file_id}
**Açıklama:** Dosya indirme veya URL alma
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `download` (boolean): Direkt indirme linki
- `thumbnail` (boolean): Küçük resim versiyonu
**Response (200):**
```json
{
  "success": true,
  "data": {
    "file_id": "file-uuid",
    "filename": "document.pdf",
    "size": 2048576,
    "mime_type": "application/pdf",
    "download_url": "https://files.markamind.com/file-uuid/download?token=temp-token",
    "expires_at": "2024-01-21T17:40:00Z",
    "metadata": {
      "created_at": "2024-01-21T16:40:00Z",
      "last_accessed": "2024-01-21T16:45:00Z",
      "access_count": 5
    }
  }
}
```

### DELETE /api/files/{file_id}
**Açıklama:** Dosyayı kalıcı olarak siler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `force` (boolean): Kullanımda olan dosyayı zorla sil
**Response (200):**
```json
{
  "success": true,
  "message": "Dosya başarıyla silindi",
  "data": {
    "file_id": "file-uuid",
    "filename": "document.pdf",
    "deleted_at": "2024-01-21T16:50:00Z",
    "storage_freed": 2048576,
    "dependencies_removed": [
      "training_data_ref_1",
      "chatbot_avatar_ref"
    ]
  }
}
```

### GET /api/files/list
**Açıklama:** Kullanıcının dosyalarını listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `category` (string): Dosya kategorisi filtresi
- `mime_type` (string): MIME türü filtresi
- `search` (string): Dosya adında arama
- `sort` (string): name, size, date, usage
- `order` (string): asc, desc
- `page` (int): Sayfa numarası
- `limit` (int): Sayfa başına kayıt
**Response (200):**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "file-uuid",
        "filename": "logo.png",
        "original_filename": "şirket_logosu.png",
        "size": 245760,
        "mime_type": "image/png",
        "category": "logo",
        "url": "https://files.markamind.com/file-uuid",
        "thumbnail_url": "https://files.markamind.com/file-uuid/thumb",
        "created_at": "2024-01-20T14:30:00Z",
        "last_accessed": "2024-01-21T15:20:00Z",
        "usage": {
          "chatbots": ["chatbot-uuid-1", "chatbot-uuid-2"],
          "access_count": 15
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_files": 48
    },
    "storage_stats": {
      "total_used": 52428800,
      "total_limit": 524288000,
      "usage_percentage": 10,
      "by_category": {
        "training_data": 35651584,
        "logos": 5242880,
        "avatars": 2621440,
        "documents": 8912896
      }
    }
  }
}
```

## 12. Webhook ve Entegrasyon

### POST /api/webhooks
**Açıklama:** Yeni webhook oluşturur
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Müşteri Sohbet Webhook",
  "url": "https://example.com/webhooks/markamind",
  "events": [
    "message.received",
    "conversation.started",
    "conversation.ended",
    "satisfaction.rated"
  ],
  "secret": "webhook-secret-key",
  "active": true,
  "retry_policy": {
    "max_retries": 3,
    "retry_delay": 5000,
    "exponential_backoff": true
  },
  "filters": {
    "chatbot_ids": ["chatbot-uuid-1"],
    "satisfaction_threshold": 3
  }
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "Webhook başarıyla oluşturuldu",
  "data": {
    "webhook_id": "webhook-uuid",
    "name": "Müşteri Sohbet Webhook",
    "url": "https://example.com/webhooks/markamind",
    "events": [
      "message.received",
      "conversation.started",
      "conversation.ended",
      "satisfaction.rated"
    ],
    "secret": "webhook-secret-key",
    "verification_status": "pending",
    "created_at": "2024-01-21T17:00:00Z"
  }
}
```

### GET /api/webhooks
**Açıklama:** Kullanıcının webhook'larını listeler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `active` (boolean): Sadece aktif webhook'lar
- `event` (string): Belirli event türü filtresi
**Response (200):**
```json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": "webhook-uuid",
        "name": "Müşteri Sohbet Webhook",
        "url": "https://example.com/webhooks/markamind",
        "events": ["message.received", "conversation.ended"],
        "active": true,
        "verification_status": "verified",
        "created_at": "2024-01-21T17:00:00Z",
        "last_triggered": "2024-01-21T16:45:00Z",
        "stats": {
          "total_deliveries": 245,
          "successful_deliveries": 242,
          "failed_deliveries": 3,
          "last_success": "2024-01-21T16:45:00Z",
          "last_failure": "2024-01-20T14:30:00Z"
        }
      }
    ],
    "total_webhooks": 3,
    "active_webhooks": 2
  }
}
```

### PUT /api/webhooks/{webhook_id}
**Açıklama:** Webhook ayarlarını günceller
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "name": "Güncellenmiş Webhook",
  "url": "https://newexample.com/webhooks/markamind",
  "events": ["message.received", "satisfaction.rated"],
  "active": true,
  "retry_policy": {
    "max_retries": 5,
    "retry_delay": 3000
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Webhook başarıyla güncellendi",
  "data": {
    "webhook_id": "webhook-uuid",
    "updated_fields": ["name", "url", "events", "retry_policy"],
    "verification_required": true,
    "updated_at": "2024-01-21T17:15:00Z"
  }
}
```

### DELETE /api/webhooks/{webhook_id}
**Açıklama:** Webhook'u siler
**Headers:** `Authorization: Bearer {token}`
**Response (200):**
```json
{
  "success": true,
  "message": "Webhook başarıyla silindi",
  "data": {
    "webhook_id": "webhook-uuid",
    "deleted_at": "2024-01-21T17:20:00Z",
    "final_stats": {
      "total_deliveries": 245,
      "successful_deliveries": 242
    }
  }
}
```

### POST /api/webhooks/{webhook_id}/test
**Açıklama:** Webhook'u test eder
**Headers:** `Authorization: Bearer {token}`
**Request Body:**
```json
{
  "event_type": "message.received",
  "test_payload": {
    "message": "Test mesajı",
    "user_id": "test-user",
    "chatbot_id": "chatbot-uuid"
  }
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Webhook test edildi",
  "data": {
    "test_id": "test-uuid",
    "webhook_id": "webhook-uuid",
    "status": "success",
    "response_time": 245,
    "response_status": 200,
    "response_headers": {
      "content-type": "application/json"
    },
    "response_body": "{\"status\":\"received\"}",
    "tested_at": "2024-01-21T17:25:00Z"
  }
}
```

## 13. İstatistik ve Monitoring

### GET /api/stats/global
**Açıklama:** Platform genelindeki istatistikleri getirir
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): today, week, month, year
- `include_trends` (boolean): Trend analizini dahil et
**Response (200):**
```json
{
  "success": true,
  "data": {
    "platform_stats": {
      "total_users": 15670,
      "active_users": 8945,
      "total_chatbots": 45623,
      "active_chatbots": 34567,
      "total_conversations": 2567890,
      "messages_today": 145670
    },
    "user_stats": {
      "your_rank": 156,
      "your_percentile": 85,
      "your_chatbots": 7,
      "your_conversations": 1250
    },
    "system_performance": {
      "average_response_time": 1.1,
      "uptime_percentage": 99.8,
      "success_rate": 98.5,
      "peak_concurrent_users": 2345
    },
    "trends": {
      "users_growth": "+12%",
      "conversations_growth": "+23%",
      "satisfaction_trend": "+0.3"
    },
    "popular_features": [
      {
        "feature": "PDF Training",
        "usage_percentage": 78
      },
      {
        "feature": "Custom Animations",
        "usage_percentage": 45
      }
    ]
  }
}
```

### GET /api/stats/user
**Açıklama:** Kullanıcı bazlı detaylı istatistikler
**Headers:** `Authorization: Bearer {token}`
**Query Parameters:**
- `period` (string): Analiz dönemi
- `compare_previous` (boolean): Önceki dönemle karşılaştırma
**Response (200):**
```json
{
  "success": true,
  "data": {
    "account_stats": {
      "account_age_days": 45,
      "subscription_plan": "professional",
      "total_spent": 897,
      "currency": "TRY"
    },
    "usage_stats": {
      "chatbots_created": 7,
      "total_conversations": 1250,
      "total_messages": 8750,
      "unique_users_served": 856,
      "training_data_uploaded_mb": 245,
      "api_calls_made": 15670
    },
    "engagement_stats": {
      "login_streak": 12,
      "last_login": "2024-01-21T16:30:00Z",
      "most_active_day": "Tuesday",
      "average_session_duration": 25.5,
      "features_used": 18,
      "total_features": 25
    },
    "performance_stats": {
      "average_satisfaction": 4.3,
      "best_performing_chatbot": "chatbot-uuid-1",
      "total_integrations": 3,
      "successful_deployments": 7
    },
    "achievements": [
      {
        "id": "first_chatbot",
        "name": "İlk Chatbot",
        "description": "İlk chatbot'unuzu oluşturdunuz",
        "unlocked_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": "satisfaction_master",
        "name": "Memnuniyet Ustası",
        "description": "4.5+ memnuniyet skoru elde ettiniz",
        "unlocked_at": "2024-01-20T14:20:00Z"
      }
    ],
    "comparison": {
      "previous_period": {
        "conversations": 945,
        "satisfaction": 4.1
      },
      "growth": {
        "conversations": "+32%",
        "satisfaction": "+0.2"
      }
    }
  }
}
```

### GET /api/monitoring/uptime
**Açıklama:** Sistem çalışma süresi ve kullanılabilirlik
**Query Parameters:**
- `period` (string): Monitoring dönemi
- `service` (string): Belirli servis filtresi
**Response (200):**
```json
{
  "success": true,
  "data": {
    "overall_uptime": {
      "percentage": 99.87,
      "total_downtime_minutes": 34,
      "last_incident": "2024-01-18T03:15:00Z",
      "mttr_minutes": 8.5
    },
    "service_uptime": [
      {
        "service": "API",
        "uptime_percentage": 99.95,
        "status": "operational",
        "last_check": "2024-01-21T17:30:00Z"
      },
      {
        "service": "AI Service",
        "uptime_percentage": 99.82,
        "status": "operational",
        "last_check": "2024-01-21T17:30:00Z"
      },
      {
        "service": "Database",
        "uptime_percentage": 99.98,
        "status": "operational",
        "last_check": "2024-01-21T17:30:00Z"
      }
    ],
    "incidents": [
      {
        "id": "incident-uuid",
        "title": "AI Service Slow Response",
        "status": "resolved",
        "severity": "minor",
        "started_at": "2024-01-18T03:15:00Z",
        "resolved_at": "2024-01-18T03:23:00Z",
        "duration_minutes": 8,
        "affected_users": 156
      }
    ],
    "sla_metrics": {
      "target_uptime": 99.9,
      "current_uptime": 99.87,
      "sla_credits_due": 0
    }
  }
}
```

### GET /api/monitoring/performance
**Açıklama:** Detaylı sistem performans metrikleri
**Query Parameters:**
- `period` (string): Monitoring dönemi
- `granularity` (string): minute, hour, day
**Response (200):**
```json
{
  "success": true,
  "data": {
    "current_metrics": {
      "requests_per_second": 45.7,
      "average_response_time": 125,
      "error_rate": 0.02,
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 23.4
    },
    "performance_timeline": [
      {
        "timestamp": "2024-01-21T17:00:00Z",
        "requests_per_second": 42.3,
        "response_time": 118,
        "error_rate": 0.01
      },
      {
        "timestamp": "2024-01-21T17:15:00Z",
        "requests_per_second": 48.9,
        "response_time": 132,
        "error_rate": 0.03
      }
    ],
    "alerts": [
      {
        "id": "alert-uuid",
        "type": "high_response_time",
        "severity": "warning",
        "message": "Ortalama yanıt süresi eşik değeri aştı",
        "threshold": 100,
        "current_value": 125,
        "triggered_at": "2024-01-21T17:25:00Z",
        "status": "active"
      }
    ],
    "peak_usage": {
      "highest_rps": {
        "value": 89.4,
        "timestamp": "2024-01-21T14:30:00Z"
      },
      "slowest_response": {
        "value": 2340,
        "timestamp": "2024-01-21T16:45:00Z",
        "endpoint": "/api/chat/message"
      }
    }
  }
}
```