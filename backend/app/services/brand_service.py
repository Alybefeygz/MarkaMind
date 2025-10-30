# -*- coding: utf-8 -*-
"""
Brand Service
Marka CRUD ve yönetim işlemleri
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from app.config.supabase import supabase
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
import logging
import re

logger = logging.getLogger(__name__)


class BrandService:
    """Brand management service"""

    @staticmethod
    def _generate_slug(name: str) -> str:
        """
        Marka adından slug oluştur

        Args:
            name: Marka adı

        Returns:
            str: URL-safe slug
        """
        # Türkçe karakterleri dönüştür
        turkish_map = {
            'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
        }

        slug = name.lower()
        for tr_char, en_char in turkish_map.items():
            slug = slug.replace(tr_char, en_char)

        # Sadece alfanumerik ve tire bırak
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug.strip('-')

        return slug

    @staticmethod
    async def create_brand(
        user_id: str,
        brand_data: BrandCreate
    ) -> BrandResponse:
        """
        Yeni marka oluştur

        Args:
            user_id: Kullanıcı ID
            brand_data: Marka bilgileri

        Returns:
            BrandResponse: Oluşturulan marka

        Raises:
            HTTPException: Oluşturma başarısız
        """
        try:
            # Slug oluştur
            base_slug = BrandService._generate_slug(brand_data.name)
            slug = base_slug

            # Slug benzersizliği kontrolü
            counter = 1
            while True:
                existing = supabase.table('brands').select('id').eq('slug', slug).execute()
                if not existing.data:
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Insert data
            insert_data = {
                'user_id': user_id,
                'name': brand_data.name,
                'slug': slug,
                'description': brand_data.description,
                'logo_url': brand_data.logo_url,
                'theme_color': brand_data.theme_color,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            result = supabase.table('brands').insert(insert_data).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Marka oluşturulamadı"
                )

            brand = result.data[0]
            logger.info(f"Brand created: {brand['id']} by user: {user_id}")

            return BrandResponse(**brand)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create brand error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Marka oluşturulurken hata: {str(e)}"
            )

    @staticmethod
    async def get_brands(
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Kullanıcının markalarını listele

        Args:
            user_id: Kullanıcı ID
            skip: Atlama sayısı (pagination)
            limit: Limit (pagination)
            is_active: Sadece aktif markaları göster

        Returns:
            List[Dict]: Marka listesi
        """
        try:
            query = supabase.table('brands').select('*').eq('user_id', user_id)

            # Filter by active status
            if is_active is not None:
                query = query.eq('is_active', is_active)

            # Pagination
            query = query.range(skip, skip + limit - 1)

            # Order by created_at desc
            query = query.order('created_at', desc=True)

            result = query.execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Get brands error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Markalar getirilirken hata: {str(e)}"
            )

    @staticmethod
    async def get_brand(
        brand_id: str,
        user_id: str
    ) -> BrandResponse:
        """
        Tek marka detayı getir

        Args:
            brand_id: Marka ID
            user_id: Kullanıcı ID

        Returns:
            BrandResponse: Marka detayı

        Raises:
            HTTPException: Marka bulunamadı
        """
        try:
            result = supabase.table('brands')\
                .select('*')\
                .eq('id', brand_id)\
                .eq('user_id', user_id)\
                .execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Marka bulunamadı"
                )

            return BrandResponse(**result.data[0])

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get brand error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Marka getirilirken hata: {str(e)}"
            )

    @staticmethod
    async def update_brand(
        brand_id: str,
        user_id: str,
        update_data: BrandUpdate
    ) -> BrandResponse:
        """
        Marka güncelle

        Args:
            brand_id: Marka ID
            user_id: Kullanıcı ID
            update_data: Güncellenecek veriler

        Returns:
            BrandResponse: Güncellenmiş marka

        Raises:
            HTTPException: Güncelleme başarısız
        """
        try:
            # Önce marka var mı ve user'a ait mi kontrol et
            existing = supabase.table('brands')\
                .select('*')\
                .eq('id', brand_id)\
                .eq('user_id', user_id)\
                .execute()

            if not existing.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Marka bulunamadı veya size ait değil"
                )

            # Sadece değişen alanları al
            update_dict = update_data.model_dump(exclude_unset=True)

            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Güncellenecek alan bulunamadı"
                )

            # Eğer name değişiyorsa slug'ı yeniden oluştur
            if 'name' in update_dict:
                base_slug = BrandService._generate_slug(update_dict['name'])
                slug = base_slug

                # Slug benzersizliği kontrolü (mevcut brand hariç)
                counter = 1
                while True:
                    check = supabase.table('brands')\
                        .select('id')\
                        .eq('slug', slug)\
                        .neq('id', brand_id)\
                        .execute()
                    if not check.data:
                        break
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                update_dict['slug'] = slug

            # Updated_at ekle
            update_dict['updated_at'] = datetime.utcnow().isoformat()

            # Güncelle
            result = supabase.table('brands')\
                .update(update_dict)\
                .eq('id', brand_id)\
                .eq('user_id', user_id)\
                .execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Marka güncellenemedi"
                )

            logger.info(f"Brand updated: {brand_id} by user: {user_id}")

            return BrandResponse(**result.data[0])

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update brand error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Marka güncellenirken hata: {str(e)}"
            )

    @staticmethod
    async def delete_brand(
        brand_id: str,
        user_id: str,
        soft_delete: bool = True
    ) -> Dict[str, Any]:
        """
        Marka sil

        Args:
            brand_id: Marka ID
            user_id: Kullanıcı ID
            soft_delete: Soft delete (is_active=false) mi yoksa hard delete mi

        Returns:
            Dict: Silme sonucu

        Raises:
            HTTPException: Silme başarısız
        """
        try:
            # Önce marka var mı ve user'a ait mi kontrol et
            existing = supabase.table('brands')\
                .select('id')\
                .eq('id', brand_id)\
                .eq('user_id', user_id)\
                .execute()

            if not existing.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Marka bulunamadı veya size ait değil"
                )

            if soft_delete:
                # Soft delete: is_active = false
                result = supabase.table('brands')\
                    .update({
                        'is_active': False,
                        'updated_at': datetime.utcnow().isoformat()
                    })\
                    .eq('id', brand_id)\
                    .eq('user_id', user_id)\
                    .execute()

                logger.info(f"Brand soft deleted: {brand_id} by user: {user_id}")

                return {
                    "message": "Marka devre dışı bırakıldı",
                    "brand_id": brand_id,
                    "deleted": False,
                    "deactivated": True
                }
            else:
                # Hard delete: veritabanından sil
                # UYARI: İlişkili veriler (stores, chatbots) de silinebilir (CASCADE)
                result = supabase.table('brands')\
                    .delete()\
                    .eq('id', brand_id)\
                    .eq('user_id', user_id)\
                    .execute()

                logger.warning(f"Brand hard deleted: {brand_id} by user: {user_id}")

                return {
                    "message": "Marka kalıcı olarak silindi",
                    "brand_id": brand_id,
                    "deleted": True,
                    "deactivated": False
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete brand error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Marka silinirken hata: {str(e)}"
            )

    @staticmethod
    async def get_brand_stats(
        brand_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Marka istatistikleri

        Args:
            brand_id: Marka ID
            user_id: Kullanıcı ID

        Returns:
            Dict: İstatistikler
        """
        try:
            # Önce marka var mı kontrol et
            brand_check = supabase.table('brands')\
                .select('id')\
                .eq('id', brand_id)\
                .eq('user_id', user_id)\
                .execute()

            if not brand_check.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Marka bulunamadı"
                )

            # Stores count
            stores = supabase.table('stores')\
                .select('id, status')\
                .eq('brand_id', brand_id)\
                .execute()

            total_stores = len(stores.data) if stores.data else 0
            active_stores = len([s for s in (stores.data or []) if s.get('status') == 'active'])

            # Chatbots count
            chatbots = supabase.table('chatbots')\
                .select('id, status')\
                .eq('brand_id', brand_id)\
                .execute()

            total_chatbots = len(chatbots.data) if chatbots.data else 0
            active_chatbots = len([c for c in (chatbots.data or []) if c.get('status') == 'published'])

            # Products count (stores üzerinden)
            total_products = 0
            if stores.data:
                for store in stores.data:
                    products = supabase.table('products')\
                        .select('id', count='exact')\
                        .eq('store_id', store['id'])\
                        .execute()
                    total_products += products.count if products.count else 0

            return {
                "total_stores": total_stores,
                "active_stores": active_stores,
                "total_chatbots": total_chatbots,
                "active_chatbots": active_chatbots,
                "total_products": total_products
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get brand stats error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"İstatistikler getirilirken hata: {str(e)}"
            )
