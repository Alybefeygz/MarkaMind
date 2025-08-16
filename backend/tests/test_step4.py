# test_step4.py
# -*- coding: utf-8 -*-
import os
import sys

def test_env_files():
    files_to_check = ['.env', '.env.example']
    all_exists = True
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"[OK] {file} mevcut")
        else:
            print(f"[FAIL] {file} bulunamadi")
            all_exists = False
    
    return all_exists

def test_env_content():
    """Test if .env contains required keys"""
    if not os.path.exists('.env'):
        print("[FAIL] .env dosyasi bulunamadi")
        return False
    
    required_keys = [
        'SUPABASE_URL',
        'SUPABASE_API_KEY', 
        'SUPABASE_ANON_KEY',
        'SECRET_KEY',
        'OPENROUTER_BASE_URL'
    ]
    
    with open('.env', 'r') as f:
        content = f.read()
    
    all_keys_found = True
    for key in required_keys:
        if key in content:
            print(f"[OK] {key} .env'de bulundu")
        else:
            print(f"[FAIL] {key} .env'de bulunamadi")
            all_keys_found = False
    
    return all_keys_found

def test_config_import():
    """Test if config.py can be imported"""
    try:
        sys.path.insert(0, os.getcwd())
        from app.config import settings
        print("[OK] app.config import edildi")
        
        # Test some config values
        if hasattr(settings, 'supabase_url'):
            print("[OK] settings.supabase_url mevcut")
        else:
            print("[FAIL] settings.supabase_url bulunamadi")
            
        if hasattr(settings, 'openrouter_base_url'):
            print("[OK] settings.openrouter_base_url mevcut")
        else:
            print("[FAIL] settings.openrouter_base_url bulunamadi")
        
        return True
    except Exception as e:
        print(f"[FAIL] Config import hatasi: {e}")
        return False

def test_main_import():
    """Test if main.py can be imported"""
    try:
        sys.path.insert(0, os.getcwd())
        from app.main import app
        print("[OK] app.main import edildi")
        
        # Test if app is FastAPI instance
        if hasattr(app, 'title'):
            print(f"[OK] FastAPI app title: {app.title}")
        else:
            print("[FAIL] FastAPI app title bulunamadi")
        
        return True
    except Exception as e:
        print(f"[FAIL] Main import hatasi: {e}")
        return False

if __name__ == "__main__":
    print("=== ADIM 4 TEST ===")
    test_env_files()
    test_env_content()  
    test_config_import()
    test_main_import()