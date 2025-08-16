# test_step3.py
# -*- coding: utf-8 -*-
import os

def test_folder_structure():
    expected_folders = [
        'app',
        'app/models',
        'app/schemas', 
        'app/routers',
        'app/services',
        'app/utils',
        'migrations',
        'tests'
    ]
    
    all_exists = True
    for folder in expected_folders:
        if os.path.exists(folder):
            print(f"[OK] {folder} klasoru mevcut")
        else:
            print(f"[FAIL] {folder} klasoru bulunamadi")
            all_exists = False
    
    return all_exists

def test_init_files():
    expected_init_files = [
        'app/__init__.py',
        'app/models/__init__.py',
        'app/schemas/__init__.py',
        'app/routers/__init__.py', 
        'app/services/__init__.py',
        'app/utils/__init__.py'
    ]
    
    all_exists = True
    for init_file in expected_init_files:
        if os.path.exists(init_file):
            print(f"[OK] {init_file} mevcut")
        else:
            print(f"[FAIL] {init_file} bulunamadi")
            all_exists = False
    
    return all_exists

def test_core_files():
    core_files = [
        'app/main.py',
        'app/config.py', 
        'app/database.py',
        'app/dependencies.py'
    ]
    
    all_exists = True
    for core_file in core_files:
        if os.path.exists(core_file):
            print(f"[OK] {core_file} mevcut")
        else:
            print(f"[FAIL] {core_file} bulunamadi") 
            all_exists = False
    
    return all_exists

def test_service_files():
    service_files = [
        'app/services/openrouter_service.py',
        'app/services/supabase_service.py',
        'app/services/auth_service.py'
    ]
    
    all_exists = True
    for service_file in service_files:
        if os.path.exists(service_file):
            print(f"[OK] {service_file} mevcut")
        else:
            print(f"[FAIL] {service_file} bulunamadi")
            all_exists = False
            
    return all_exists

if __name__ == "__main__":
    print("=== ADIM 3 TEST ===")
    test_folder_structure()
    test_init_files()
    test_core_files()
    test_service_files()