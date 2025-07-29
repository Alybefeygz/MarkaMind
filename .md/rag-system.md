# MarkaMind RAG (Retrieval-Augmented Generation) Sistemi

## 1. RAG Sistemi Genel Bakış

RAG (Retrieval-Augmented Generation), MarkaMind platformunda chatbot'ların kullanıcı sorgularına daha doğru ve ilgili yanıtlar verebilmesi için tasarlanmış bir sistemdir. Bu sistem, chatbot'ların eğitim verilerini vektörleştirerek semantik arama yapabilmelerini ve bu bilgileri kullanarak daha kaliteli yanıtlar üretebilmelerini sağlar.

### 1.1 RAG Sistemi Bileşenleri

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Sistem Mimarisi                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   İçerik    │ ─► │   Chunking  │ ─► │ Embedding   │     │
│  │  İşleme     │    │   İşlemi    │    │  Oluşturma  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    PDF      │    │   Chunks    │    │   Vector    │     │
│  │   Text      │    │ (1000 char) │    │  Database   │     │
│  │    URL      │    │             │    │ (ChromaDB)  │     │
│  │   Manual    │    │             │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Sorgu İşleme Süreci                   │   │
│  │                                                     │   │
│  │  User Query ─► Embedding ─► Similarity Search ─►   │   │
│  │                                                     │   │
│  │  Retrieved Context ─► LLM ─► Generated Response    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 2. RAG Sistemi Çalışma Süreci

### 2.1 Eğitim Verisi Hazırlama

#### Adım 1: İçerik Toplama
```python
# Desteklenen veri kaynakları
data_sources = {
    "pdf": "PDF dökümanları",
    "text": "Metin dosyaları (.txt, .docx, .md)",
    "url": "Web sayfaları",
    "manual": "Manuel metin girişleri"
}
```

#### Adım 2: Metin Çıkarma ve Temizleme
```python
# PDF işleme örneği
def extract_text_from_pdf(file_path: str) -> str:
    """PDF'den metin çıkarma ve temizleme"""
    # PyPDF2 veya pdfplumber kullanarak metin çıkarma
    # Gereksiz boşlukları ve özel karakterleri temizleme
    # Metin kalitesini artırma işlemleri
    pass
```

#### Adım 3: Chunking (Parçalama)
```python
# Metin parçalama konfigürasyonu
CHUNK_CONFIG = {
    "chunk_size": 1000,      # Her chunk maksimum 1000 karakter
    "chunk_overlap": 200,    # Chunklar arası 200 karakter örtüşme
    "separators": ["\n\n", "\n", ". ", " "],  # Ayırıcı karakterler
}

def create_chunks(text: str) -> List[str]:
    """Metni anlam bütünlüğünü koruyarak parçalara ayırma"""
    # Recursive character splitting
    # Sentence boundary korunması
    # Paragraph structure muhafaza edilmesi
    pass
```

### 2.2 Embedding Oluşturma

#### Embedding Model Seçimi
```python
# OpenAI Ada-002 Embedding Model
EMBEDDING_CONFIG = {
    "model": "text-embedding-ada-002",
    "dimensions": 1536,
    "max_tokens": 8191,
    "cost_per_1k_tokens": 0.0001
}

async def create_embedding(text: str) -> List[float]:
    """Metin için embedding vektörü oluşturma"""
    response = await openai.Embedding.acreate(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']
```

### 2.3 Vektör Veritabanı Yönetimi

#### ChromaDB Konfigürasyonu
```python
# ChromaDB setup
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

def create_collection(chatbot_id: str) -> chromadb.Collection:
    """Chatbot için collection oluşturma"""
    collection_name = f"chatbot_{chatbot_id}"
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection
```

#### Vektör Depolama
```python
def store_embeddings(collection: chromadb.Collection, chunks: List[dict]):
    """Embedding'leri veritabanında saklama"""
    ids = [chunk["id"] for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
```

### 2.4 Semantik Arama

#### Benzerlik Arama
```python
async def similarity_search(
    collection: chromadb.Collection,
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.7
) -> List[dict]:
    """Sorgu için en benzer chunk'ları bulma"""
    
    # Query embedding oluşturma
    query_embedding = await create_embedding(query)
    
    # Benzerlik araması
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"similarity": {"$gte": similarity_threshold}}
    )
    
    return format_search_results(results)
```

#### Context Hazırlama
```python
def prepare_context(search_results: List[dict], max_context_length: int = 3000) -> str:
    """Arama sonuçlarından context hazırlama"""
    context_parts = []
    current_length = 0
    
    for result in search_results:
        text = result["document"]
        if current_length + len(text) > max_context_length:
            break
        context_parts.append(text)
        current_length += len(text)
    
    return "\n\n".join(context_parts)
```

## 3. RAG Pipeline Implementation

### 3.1 RAG Service Sınıfı
```python
# app/services/rag_service.py
from typing import List, Dict, Optional
import asyncio
from app.core.config import settings
from app.repositories.rag_repository import RAGRepository

class RAGService:
    def __init__(self):
        self.repository = RAGRepository()
        self.embedding_model = settings.RAG_EMBEDDING_MODEL
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP
    
    async def process_training_data(
        self, 
        chatbot_id: int, 
        data_id: str,
        content: str,
        source_type: str
    ) -> Dict:
        """Eğitim verisini işleme ve embedding oluşturma"""
        
        # 1. Metin parçalama
        chunks = self.create_chunks(content)
        
        # 2. Her chunk için embedding oluşturma
        chunk_data = []
        for i, chunk_text in enumerate(chunks):
            embedding = await self.create_embedding(chunk_text)
            chunk_data.append({
                "chatbot_id": chatbot_id,
                "data_id": data_id,
                "chunk_index": i,
                "text": chunk_text,
                "embedding": embedding,
                "source_type": source_type,
                "metadata": {
                    "chunk_size": len(chunk_text),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
        
        # 3. Veritabanına kaydetme
        result = await self.repository.store_chunks(chunk_data)
        
        return {
            "total_chunks": len(chunks),
            "embeddings_created": len(chunk_data),
            "data_id": data_id
        }
    
    async def semantic_search(
        self,
        chatbot_id: int,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Semantik arama gerçekleştirme"""
        
        # 1. Query embedding oluşturma
        query_embedding = await self.create_embedding(query)
        
        # 2. Benzerlik araması
        search_results = await self.repository.similarity_search(
            chatbot_id=chatbot_id,
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filters=filters
        )
        
        return search_results
    
    async def generate_response(
        self,
        chatbot_id: int,
        user_query: str,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict:
        """RAG ile yanıt oluşturma"""
        
        # 1. Semantik arama
        relevant_chunks = await self.semantic_search(
            chatbot_id=chatbot_id,
            query=user_query
        )
        
        # 2. Context hazırlama
        context = self.prepare_context(relevant_chunks)
        
        # 3. Prompt oluşturma
        prompt = self.create_prompt(user_query, context, chat_history)
        
        # 4. LLM ile yanıt oluşturma
        response = await self.generate_llm_response(prompt)
        
        return {
            "response": response,
            "sources": relevant_chunks,
            "context_used": context,
            "confidence": self.calculate_confidence(relevant_chunks)
        }
```

### 3.2 RAG Repository
```python
# app/repositories/rag_repository.py
from typing import List, Dict, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.models.rag_chunk import RAGChunk
from app.models.rag_embedding import RAGEmbedding

class RAGRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def store_chunks(self, chunk_data: List[Dict]) -> Dict:
        """Chunk'ları ve embedding'leri veritabanında saklama"""
        stored_chunks = []
        
        for chunk in chunk_data:
            # Chunk kaydı
            db_chunk = RAGChunk(
                chatbot_id=chunk["chatbot_id"],
                data_id=chunk["data_id"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                source_type=chunk["source_type"],
                metadata=chunk["metadata"]
            )
            self.db.add(db_chunk)
            self.db.flush()
            
            # Embedding kaydı
            db_embedding = RAGEmbedding(
                chunk_id=db_chunk.id,
                embedding=chunk["embedding"],
                model=settings.RAG_EMBEDDING_MODEL,
                dimension=len(chunk["embedding"])
            )
            self.db.add(db_embedding)
            stored_chunks.append(db_chunk.id)
        
        self.db.commit()
        return {"stored_chunks": len(stored_chunks)}
    
    async def similarity_search(
        self,
        chatbot_id: int,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Cosine similarity ile arama"""
        
        # Vector similarity hesaplama
        query = self.db.query(RAGChunk, RAGEmbedding).join(
            RAGEmbedding, RAGChunk.id == RAGEmbedding.chunk_id
        ).filter(RAGChunk.chatbot_id == chatbot_id)
        
        # Filtreler uygulama
        if filters:
            if filters.get("source_type"):
                query = query.filter(RAGChunk.source_type.in_(filters["source_type"]))
        
        results = query.all()
        
        # Similarity skorları hesaplama
        scored_results = []
        query_vector = np.array(query_embedding)
        
        for chunk, embedding in results:
            embedding_vector = np.array(embedding.embedding)
            similarity = np.dot(query_vector, embedding_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(embedding_vector)
            )
            
            if similarity >= similarity_threshold:
                scored_results.append({
                    "chunk_id": chunk.id,
                    "text": chunk.text,
                    "similarity_score": float(similarity),
                    "source_type": chunk.source_type,
                    "metadata": chunk.metadata
                })
        
        # Similarity skoruna göre sıralama
        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_results[:top_k]
```

## 4. RAG Database Models

### 4.1 RAG Chunk Model
```python
# app/models/rag_chunk.py
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RAGChunk(BaseModel):
    __tablename__ = "rag_chunks"
    
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    data_id = Column(String(255), nullable=False)  # training_data table reference
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)  # pdf, text, url, manual
    metadata = Column(JSON, default={})
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="rag_chunks")
    embeddings = relationship("RAGEmbedding", back_populates="chunk", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_chatbot_chunk', 'chatbot_id', 'chunk_index'),
        Index('idx_data_source', 'data_id', 'source_type'),
    )
```

### 4.2 RAG Embedding Model
```python
# app/models/rag_embedding.py
from sqlalchemy import Column, Integer, String, ARRAY, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RAGEmbedding(BaseModel):
    __tablename__ = "rag_embeddings"
    
    chunk_id = Column(Integer, ForeignKey("rag_chunks.id"), nullable=False, unique=True)
    embedding = Column(ARRAY(Float), nullable=False)
    model = Column(String(100), nullable=False)  # embedding model name
    dimension = Column(Integer, nullable=False)
    
    # Relationships
    chunk = relationship("RAGChunk", back_populates="embeddings")
    
    # Indexes for vector search optimization
    __table_args__ = (
        Index('idx_embedding_chunk', 'chunk_id'),
        # Vector similarity index (PostgreSQL with pgvector extension)
        # Index('idx_embedding_vector', 'embedding', postgresql_using='ivfflat'),
    )
```

## 5. RAG Optimization Strategies

### 5.1 Chunk Optimization
```python
def optimize_chunks(chatbot_id: int) -> Dict:
    """Chunk kalitesini artırma işlemleri"""
    optimizations = {
        "remove_duplicates": remove_duplicate_chunks(chatbot_id),
        "merge_similar": merge_similar_chunks(chatbot_id),
        "remove_low_quality": remove_low_quality_chunks(chatbot_id),
        "update_metadata": update_chunk_metadata(chatbot_id)
    }
    return optimizations

def remove_duplicate_chunks(chatbot_id: int) -> int:
    """Duplicate chunk'ları kaldırma"""
    # Cosine similarity > 0.95 olan chunk'ları bulma
    # Text similarity kontrolü
    # Metadata karşılaştırması
    pass

def merge_similar_chunks(chatbot_id: int, threshold: float = 0.9) -> int:
    """Benzer chunk'ları birleştirme"""
    # Ardışık ve benzer chunk'ları tespit etme
    # Context bütünlüğünü koruyarak birleştirme
    pass
```

### 5.2 Index Optimization
```python
def rebuild_vector_index(chatbot_id: int) -> Dict:
    """Vektör index'ini yeniden oluşturma"""
    # FAISS index kullanımı
    import faiss
    
    # Embedding'leri yükleme
    embeddings = load_embeddings(chatbot_id)
    embedding_matrix = np.array([emb.embedding for emb in embeddings])
    
    # FAISS index oluşturma
    dimension = embedding_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product index
    index.add(embedding_matrix.astype('float32'))
    
    # Index'i kaydetme
    faiss.write_index(index, f"indexes/chatbot_{chatbot_id}.index")
    
    return {
        "index_size": embedding_matrix.shape[0],
        "dimension": dimension,
        "index_type": "FAISS_FlatIP"
    }
```

## 6. RAG Performance Monitoring

### 6.1 Kalite Metrikleri
```python
class RAGQualityMetrics:
    def __init__(self, chatbot_id: int):
        self.chatbot_id = chatbot_id
    
    def calculate_retrieval_metrics(self, queries: List[str]) -> Dict:
        """Retrieval kalite metrikleri"""
        metrics = {
            "average_similarity": 0.0,
            "context_relevance": 0.0,
            "coverage_percentage": 0.0,
            "response_time_ms": 0.0
        }
        
        total_similarity = 0
        total_queries = len(queries)
        
        for query in queries:
            start_time = time.time()
            results = self.semantic_search(query)
            end_time = time.time()
            
            if results:
                avg_similarity = sum(r["similarity_score"] for r in results) / len(results)
                total_similarity += avg_similarity
            
            metrics["response_time_ms"] += (end_time - start_time) * 1000
        
        metrics["average_similarity"] = total_similarity / total_queries
        metrics["response_time_ms"] = metrics["response_time_ms"] / total_queries
        
        return metrics
```

### 6.2 Performans İzleme
```python
def monitor_rag_performance(chatbot_id: int, period_days: int = 7) -> Dict:
    """RAG sistem performansını izleme"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    # Query logs analizi
    query_logs = get_query_logs(chatbot_id, start_date, end_date)
    
    performance_metrics = {
        "total_queries": len(query_logs),
        "average_response_time": calculate_avg_response_time(query_logs),
        "cache_hit_rate": calculate_cache_hit_rate(query_logs),
        "user_satisfaction": calculate_satisfaction_score(query_logs),
        "frequent_queries": get_frequent_queries(query_logs),
        "low_confidence_queries": get_low_confidence_queries(query_logs)
    }
    
    return performance_metrics
```

## 7. RAG Best Practices

### 7.1 Chunk Strategy
- **Optimal Chunk Size**: 500-1000 karakter arası
- **Overlap**: %10-20 oranında örtüşme
- **Semantic Boundaries**: Cümle ve paragraf sınırlarına saygı
- **Context Preservation**: İlgili bilgilerin aynı chunk'ta kalması

### 7.2 Embedding Strategy
- **Model Selection**: Task'a uygun embedding model seçimi
- **Batch Processing**: Performans için batch embedding oluşturma
- **Caching**: Sık kullanılan embedding'leri cache'leme
- **Version Control**: Embedding model versiyonlarını takip etme

### 7.3 Search Strategy
- **Hybrid Search**: Semantic + keyword search kombinasyonu
- **Reranking**: Sonuçları context'e göre yeniden sıralama
- **Filtering**: Metadata tabanlı filtreleme
- **Dynamic K**: Query complexity'ye göre dinamik top-k

### 7.4 Quality Assurance
- **Regular Evaluation**: Retrieval kalitesini düzenli ölçme
- **User Feedback**: Kullanıcı geri bildirimlerini entegre etme
- **A/B Testing**: Farklı RAG stratejilerini test etme
- **Continuous Improvement**: Sürekli optimizasyon

## 8. RAG Error Handling

### 8.1 Common Issues
```python
class RAGErrorHandler:
    @staticmethod
    def handle_embedding_errors(error: Exception, retry_count: int = 3):
        """Embedding oluşturma hatalarını yönetme"""
        if "rate_limit" in str(error).lower():
            time.sleep(2 ** retry_count)  # Exponential backoff
            return True  # Retry
        elif "token_limit" in str(error).lower():
            # Chunk'ı daha küçük parçalara böl
            return "split_chunk"
        return False  # Don't retry
    
    @staticmethod
    def handle_search_errors(error: Exception):
        """Arama hatalarını yönetme"""
        if "index_not_found" in str(error).lower():
            # Index'i yeniden oluştur
            return "rebuild_index"
        elif "dimension_mismatch" in str(error).lower():
            # Embedding model değişikliği
            return "update_embeddings"
        return "fallback_search"
```

### 8.2 Fallback Strategies
```python
def fallback_search_strategy(query: str, chatbot_id: int) -> List[Dict]:
    """RAG başarısız olduğunda fallback arama"""
    # 1. Simple text search
    # 2. Fuzzy matching
    # 3. Keyword extraction
    # 4. Default responses
    pass
```

Bu RAG sistemi, MarkaMind platformunda chatbot'ların daha akıllı ve context-aware yanıtlar verebilmesini sağlayacak, kullanıcı deneyimini önemli ölçüde artıracaktır.