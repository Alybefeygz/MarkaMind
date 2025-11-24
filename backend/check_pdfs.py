from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_API_KEY")
)

print("=" * 70)
print("TÜM CHATBOX'LAR (En Yeniden Eskiye):")
print("=" * 70)

chatboxes = supabase.table("chatbots").select("id, name, created_at").order("created_at", desc=True).execute()

for cb in chatboxes.data:
    print(f"\n📦 {cb['name']}")
    print(f"   ID: {cb['id']}")
    print(f"   Oluşturma: {cb['created_at']}")
    
    # Bu chatbox'a bağlı PDF'leri getir
    pdfs = supabase.table("knowledge_base_entries").select("id, source_name, created_at").eq("chatbot_id", cb['id']).order("created_at", desc=True).execute()
    
    if pdfs.data:
        print(f"   📄 PDF'ler ({len(pdfs.data)} adet):")
        for pdf in pdfs.data:
            print(f"      - {pdf['source_name']} (Yükleme: {pdf['created_at']})")
    else:
        print(f"   ❌ PDF yok")

print("\n" + "=" * 70)
print("SON YÜKLENEN PDF'LER:")
print("=" * 70)

all_pdfs = supabase.table("knowledge_base_entries").select("id, source_name, chatbot_id, created_at").order("created_at", desc=True).limit(10).execute()

for pdf in all_pdfs.data:
    # Chatbox adını bul
    cb = supabase.table("chatbots").select("name").eq("id", pdf['chatbot_id']).execute()
    cb_name = cb.data[0]['name'] if cb.data else "❌ Bilinmeyen"
    
    print(f"\n📄 {pdf['source_name']}")
    print(f"   Bağlı Chatbox: {cb_name}")
    print(f"   Chatbox ID: {pdf['chatbot_id']}")
    print(f"   PDF ID: {pdf['id']}")
    print(f"   Yüklenme: {pdf['created_at']}")

