"""
One-time Migration Script
Chunk all existing PDFs in knowledge_base_entries
"""
import asyncio
from app.config.settings import settings
from app.services.chunking_service import chunking_service
from supabase import create_client, Client


async def migrate_existing_pdfs():
    """Chunk all existing PDFs that don't have chunks yet"""

    print("=" * 60)
    print("📚 CHUNKING MIGRATION SCRIPT")
    print("=" * 60)
    print()

    # Initialize Supabase client (using service role key for admin access)
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

    # 1. Get all knowledge base entries with content
    print("🔍 Mevcut PDF'leri buluyorum...")
    result = supabase.table("knowledge_base_entries").select(
        "id, chatbot_id, source_name, content, status"
    ).not_.is_("content", "null").execute()

    if not result.data:
        print("❌ Hiç PDF bulunamadı!")
        return

    total_pdfs = len(result.data)
    print(f"✅ {total_pdfs} adet PDF bulundu\n")

    # Statistics
    already_chunked = 0
    successfully_chunked = 0
    failed = 0
    total_chunks_created = 0

    # 2. Process each PDF
    for idx, entry in enumerate(result.data, 1):
        source_id = entry["id"]
        source_name = entry.get("source_name", "unknown.pdf")
        content = entry.get("content", "")

        print(f"[{idx}/{total_pdfs}] 📄 {source_name}")

        # Check if already chunked
        existing_chunks = supabase.table("knowledge_chunks").select(
            "id", count="exact"
        ).eq("knowledge_entry_id", source_id).execute()

        if existing_chunks.count and existing_chunks.count > 0:
            print(f"  ⏭️  Zaten chunk'lanmış ({existing_chunks.count} chunk)")
            already_chunked += 1
            continue

        # Check content
        if not content or len(content.strip()) < 100:
            print(f"  ⚠️  İçerik çok kısa veya boş, atlanıyor")
            failed += 1
            continue

        try:
            # Chunk the text
            chunks = chunking_service.chunk_text(
                text=content,
                source_name=source_name
            )

            if not chunks:
                print(f"  ❌ Chunk oluşturulamadı")
                failed += 1
                continue

            # Prepare chunk records
            chunk_records = []
            for chunk in chunks:
                chunk_records.append({
                    "knowledge_entry_id": source_id,
                    "chatbot_id": entry["chatbot_id"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "token_count": chunk["token_count"],
                    "metadata": chunk["metadata"]
                })

            # Insert chunks
            insert_result = supabase.table("knowledge_chunks").insert(chunk_records).execute()

            if insert_result.data:
                chunks_count = len(insert_result.data)
                total_chunks_created += chunks_count
                print(f"  ✅ {chunks_count} chunk oluşturuldu")
                successfully_chunked += 1
            else:
                print(f"  ❌ Database insert hatası")
                failed += 1

        except Exception as e:
            print(f"  ❌ Hata: {str(e)}")
            failed += 1

        print()

    # 3. Print summary
    print("=" * 60)
    print("📊 ÖZET")
    print("=" * 60)
    print(f"Toplam PDF:           {total_pdfs}")
    print(f"Zaten chunk'lanmış:   {already_chunked}")
    print(f"Başarıyla chunk'landı: {successfully_chunked}")
    print(f"Başarısız:            {failed}")
    print(f"Toplam chunk oluştu:  {total_chunks_created}")
    print("=" * 60)
    print()

    if successfully_chunked > 0:
        print(f"✅ Migration başarılı! {successfully_chunked} PDF chunk'landı.")
    else:
        print("⚠️ Hiçbir yeni PDF chunk'lanmadı.")


if __name__ == "__main__":
    asyncio.run(migrate_existing_pdfs())
