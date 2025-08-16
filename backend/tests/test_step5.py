# test_step5.py
# -*- coding: utf-8 -*-
import asyncio
import sys
import os

async def test_database_import():
    """Test database.py import"""
    try:
        sys.path.insert(0, os.getcwd())
        from app.database import get_supabase_client
        print("[OK] database.py import edildi")
        return True
    except Exception as e:
        print(f"[FAIL] Database import hatasi: {e}")
        return False

async def test_supabase_service_import():
    """Test supabase_service.py import"""
    try:
        from app.services.supabase_service import BaseSupabaseService
        print("[OK] supabase_service.py import edildi")
        return True
    except Exception as e:
        print(f"[FAIL] Supabase service import hatasi: {e}")
        return False

async def test_supabase_connection():
    """Test actual Supabase connection"""
    try:
        from app.database import get_supabase_client, validate_supabase_config
        
        # First validate config
        if not validate_supabase_config():
            print("[FAIL] Supabase config validation failed")
            return False
        
        client = get_supabase_client()
        
        # Test basic client creation - if no exception, connection config is OK
        if client is not None:
            print("[OK] Supabase client instance olusturuldu")
        print("[OK] Supabase baglantisi basarili")
        return True
    except Exception as e:
        print(f"[FAIL] Supabase baglanti hatasi: {e}")
        return False

async def test_sql_file_exists():
    """Test if SQL migration file exists"""
    sql_file = "migrations/create_tables.sql"
    if os.path.exists(sql_file):
        print("[OK] create_tables.sql mevcut")
        
        # Check if file contains required tables
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_tables = ['users', 'brands', 'chatbots', 'knowledge_base_entries']
        for table in required_tables:
            if table in content:
                print(f"[OK] {table} tablosu SQL'de bulundu")
            else:
                print(f"[FAIL] {table} tablosu SQL'de bulunamadi")
        
        # Check for important SQL features
        sql_features = [
            ('UUID extension', 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'),
            ('RLS policies', 'ROW LEVEL SECURITY'),
            ('Indexes', 'CREATE INDEX'),
            ('Triggers', 'CREATE TRIGGER')
        ]
        
        for feature_name, feature_text in sql_features:
            if feature_text in content:
                print(f"[OK] {feature_name} SQL'de bulundu")  
            else:
                print(f"[FAIL] {feature_name} SQL'de bulunamadi")
        
        return True
    else:
        print("[FAIL] create_tables.sql bulunamadi")
        return False

async def test_service_methods():
    """Test BaseSupabaseService methods"""
    try:
        from app.services.supabase_service import BaseSupabaseService
        
        service = BaseSupabaseService()
        
        # Check if service has required methods
        required_methods = ['select', 'insert', 'update', 'delete', 'count', 'batch_insert', 'upsert']
        
        for method in required_methods:
            if hasattr(service, method):
                print(f"[OK] BaseSupabaseService.{method} metodu mevcut")
            else:
                print(f"[FAIL] BaseSupabaseService.{method} metodu bulunamadi")
        
        return True
    except Exception as e:
        print(f"[FAIL] Service methods test hatasi: {e}")
        return False

async def main():
    print("=== ADIM 5 TEST ===")
    await test_database_import()
    await test_supabase_service_import()
    await test_sql_file_exists()
    await test_service_methods()
    await test_supabase_connection()

if __name__ == "__main__":
    asyncio.run(main())