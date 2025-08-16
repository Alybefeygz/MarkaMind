# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List
from supabase import Client
from app.database import get_supabase_client
import logging
import asyncio

logger = logging.getLogger(__name__)


class BaseSupabaseService:
    """Base service class for Supabase operations"""
    
    def __init__(self):
        self.client: Client = get_supabase_client()
    
    async def select(
        self, 
        table: str, 
        columns: str = "*", 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Select data from a table"""
        try:
            query = self.client.table(table).select(columns)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            result = await asyncio.to_thread(query.execute)
            logger.info(f"Successfully selected from {table}")
            return result
            
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            raise

    async def insert(
        self, 
        table: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Insert data into a table"""
        try:
            result = await asyncio.to_thread(
                self.client.table(table).insert(data).execute
            )
            logger.info(f"Successfully inserted into {table}")
            return result
            
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}")
            raise

    async def update(
        self, 
        table: str, 
        data: Dict[str, Any], 
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update data in a table"""
        try:
            query = self.client.table(table).update(data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = await asyncio.to_thread(query.execute)
            logger.info(f"Successfully updated {table}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating {table}: {e}")
            raise

    async def delete(
        self, 
        table: str, 
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delete data from a table"""
        try:
            query = self.client.table(table).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = await asyncio.to_thread(query.execute)
            logger.info(f"Successfully deleted from {table}")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting from {table}: {e}")
            raise

    async def count(
        self, 
        table: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records in a table"""
        try:
            query = self.client.table(table).select("*", count="exact")
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = await asyncio.to_thread(query.execute)
            count = result.count if hasattr(result, 'count') else 0
            logger.info(f"Successfully counted {table}: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting {table}: {e}")
            raise

    async def execute_rpc(
        self, 
        function_name: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a PostgreSQL function"""
        try:
            if params:
                result = await asyncio.to_thread(
                    self.client.rpc(function_name, params).execute
                )
            else:
                result = await asyncio.to_thread(
                    self.client.rpc(function_name).execute
                )
            
            logger.info(f"Successfully executed RPC: {function_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing RPC {function_name}: {e}")
            raise

    async def batch_insert(
        self, 
        table: str, 
        data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Insert multiple records at once"""
        try:
            result = await asyncio.to_thread(
                self.client.table(table).insert(data_list).execute
            )
            logger.info(f"Successfully batch inserted {len(data_list)} records into {table}")
            return result
            
        except Exception as e:
            logger.error(f"Error batch inserting into {table}: {e}")
            raise

    async def upsert(
        self, 
        table: str, 
        data: Dict[str, Any],
        on_conflict: str = "id"
    ) -> Dict[str, Any]:
        """Insert or update data (upsert)"""
        try:
            result = await asyncio.to_thread(
                self.client.table(table).upsert(data, on_conflict=on_conflict).execute
            )
            logger.info(f"Successfully upserted into {table}")
            return result
            
        except Exception as e:
            logger.error(f"Error upserting into {table}: {e}")
            raise