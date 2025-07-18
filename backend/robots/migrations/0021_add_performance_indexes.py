# Generated by Django 5.1.6 on 2025-07-10 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0020_add_robot_system_prompts'),
    ]

    operations = [
        # ⚡ PERFORMANS OPTİMİZASYONU: Database indeksleri ekle
        
        # Robot tablosu için brand_id index (zaten foreign key olduğu için var olabilir)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_robot_brand_active ON robots_robot(brand_id) WHERE brand_id IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_robot_brand_active;"
        ),
        
        # RobotPDF tablosu için composite indeksler
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_robotpdf_robot_active ON robots_robotpdf(robot_id, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_robotpdf_robot_active;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_robotpdf_type_active ON robots_robotpdf(pdf_type, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_robotpdf_type_active;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_robotpdf_active_only ON robots_robotpdf(is_active) WHERE is_active = true;",
            reverse_sql="DROP INDEX IF EXISTS idx_robotpdf_active_only;"
        ),
        
        # Brand tablosu için tarih aralığı sorguları için index
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_brand_package_dates ON robots_brand(paket_baslangic_tarihi, paket_bitis_tarihi);",
            reverse_sql="DROP INDEX IF EXISTS idx_brand_package_dates;"
        ),
        
        # RobotPDF dosya adı arama için index
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_robotpdf_dosya_adi ON robots_robotpdf(dosya_adi);",
            reverse_sql="DROP INDEX IF EXISTS idx_robotpdf_dosya_adi;"
        ),
    ]
