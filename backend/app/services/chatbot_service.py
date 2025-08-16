from supabase import Client
from typing import Dict, Optional, Any, List
import uuid
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Chatbot business logic service
    
    Handles chatbot creation, management, configuration, and analytics.
    Provides centralized business logic for chatbot operations.
    """
    
    def __init__(self, supabase_client: Optional[Client] = None):
        """
        Initialize ChatbotService
        
        Args:
            supabase_client: Supabase client instance
        """
        self.supabase_client = supabase_client
        logger.info("ChatbotService initialized")
    
    async def create_chatbot(self, brand_id: str, chatbot_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create a new chatbot with business logic validation
        
        Args:
            brand_id: UUID of the brand
            chatbot_data: Chatbot creation data
            user_id: ID of the user creating the chatbot
            
        Returns:
            Created chatbot data
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Creating chatbot for brand {brand_id} by user {user_id}")
            
            # Validate brand ownership
            if not await self.validate_brand_permissions(user_id, brand_id):
                raise ValueError("User does not have permission to create chatbots for this brand")
            
            # Generate unique script token
            script_token = self.generate_script_token()
            
            # Prepare chatbot data with defaults
            chatbot_data.update({
                "brand_id": brand_id,
                "script_token": script_token,
                "status": "draft",
                "created_at": datetime.utcnow().isoformat()
            })
            
            # Insert into database
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").insert(chatbot_data).execute()
                
                if not result.data:
                    raise Exception("Failed to create chatbot in database")
                
                created_chatbot = result.data[0]
                logger.info(f"Chatbot created successfully: {created_chatbot['id']}")
                return created_chatbot
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to create chatbot: {str(e)}")
            raise Exception(f"Failed to create chatbot: {str(e)}")
    
    async def update_chatbot(self, chatbot_id: str, update_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Update chatbot with permission validation
        
        Args:
            chatbot_id: UUID of the chatbot
            update_data: Data to update
            user_id: ID of the user updating the chatbot
            
        Returns:
            Updated chatbot data
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Updating chatbot {chatbot_id} by user {user_id}")
            
            # Validate chatbot permissions
            if not await self.validate_chatbot_permissions(user_id, chatbot_id):
                raise ValueError("User does not have permission to update this chatbot")
            
            # Remove fields that shouldn't be updated directly
            forbidden_fields = ["id", "script_token", "created_at"]
            for field in forbidden_fields:
                update_data.pop(field, None)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update in database
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").update(update_data).eq("id", chatbot_id).execute()
                
                if not result.data:
                    raise Exception("Failed to update chatbot in database")
                
                updated_chatbot = result.data[0]
                logger.info(f"Chatbot updated successfully: {chatbot_id}")
                return updated_chatbot
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update chatbot: {str(e)}")
            raise Exception(f"Failed to update chatbot: {str(e)}")
    
    async def delete_chatbot(self, chatbot_id: str, user_id: str) -> bool:
        """
        Delete chatbot with permission validation
        
        Args:
            chatbot_id: UUID of the chatbot
            user_id: ID of the user deleting the chatbot
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Deleting chatbot {chatbot_id} by user {user_id}")
            
            # Validate chatbot permissions
            if not await self.validate_chatbot_permissions(user_id, chatbot_id):
                raise ValueError("User does not have permission to delete this chatbot")
            
            # Check for active conversations (optional business rule)
            if self.supabase_client:
                conversations = self.supabase_client.table("conversations").select("id").eq("chatbot_id", chatbot_id).limit(1).execute()
                
                if conversations.data:
                    logger.warning(f"Deleting chatbot {chatbot_id} with existing conversations")
            
            # Delete from database (cascade will handle related records)
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").delete().eq("id", chatbot_id).execute()
                
                if not result.data:
                    raise Exception("Failed to delete chatbot from database")
                
                logger.info(f"Chatbot deleted successfully: {chatbot_id}")
                return True
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete chatbot: {str(e)}")
            raise Exception(f"Failed to delete chatbot: {str(e)}")
    
    async def activate_chatbot(self, chatbot_id: str, user_id: str) -> bool:
        """
        Activate chatbot with validation
        
        Args:
            chatbot_id: UUID of the chatbot
            user_id: ID of the user activating the chatbot
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Activating chatbot {chatbot_id} by user {user_id}")
            
            # Validate chatbot permissions
            if not await self.validate_chatbot_permissions(user_id, chatbot_id):
                raise ValueError("User does not have permission to activate this chatbot")
            
            # Check if chatbot has required configuration
            chatbot = await self.get_chatbot_by_id(chatbot_id)
            if not chatbot:
                raise ValueError("Chatbot not found")
            
            # Business rule: Check if chatbot has at least basic configuration
            required_fields = ["name", "primary_color"]
            missing_fields = [field for field in required_fields if not chatbot.get(field)]
            
            if missing_fields:
                raise ValueError(f"Chatbot missing required fields for activation: {missing_fields}")
            
            # Update status to active
            update_data = {
                "status": "active",
                "activated_at": datetime.utcnow().isoformat()
            }
            
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").update(update_data).eq("id", chatbot_id).execute()
                
                if not result.data:
                    raise Exception("Failed to activate chatbot")
                
                logger.info(f"Chatbot activated successfully: {chatbot_id}")
                return True
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to activate chatbot: {str(e)}")
            raise Exception(f"Failed to activate chatbot: {str(e)}")
    
    async def deactivate_chatbot(self, chatbot_id: str, user_id: str) -> bool:
        """
        Deactivate chatbot
        
        Args:
            chatbot_id: UUID of the chatbot
            user_id: ID of the user deactivating the chatbot
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Deactivating chatbot {chatbot_id} by user {user_id}")
            
            # Validate chatbot permissions
            if not await self.validate_chatbot_permissions(user_id, chatbot_id):
                raise ValueError("User does not have permission to deactivate this chatbot")
            
            # Update status to draft
            update_data = {
                "status": "draft",
                "deactivated_at": datetime.utcnow().isoformat()
            }
            
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").update(update_data).eq("id", chatbot_id).execute()
                
                if not result.data:
                    raise Exception("Failed to deactivate chatbot")
                
                logger.info(f"Chatbot deactivated successfully: {chatbot_id}")
                return True
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to deactivate chatbot: {str(e)}")
            raise Exception(f"Failed to deactivate chatbot: {str(e)}")
    
    def generate_script_token(self) -> str:
        """
        Generate unique script token for chatbot widget
        
        Returns:
            Unique script token string
        """
        try:
            # Generate UUID-based token
            token = str(uuid.uuid4())
            logger.debug(f"Generated script token: {token[:8]}...")
            return token
        except Exception as e:
            logger.error(f"Failed to generate script token: {str(e)}")
            raise Exception(f"Failed to generate script token: {str(e)}")
    
    async def get_chatbot_config(self, script_token: str) -> Dict[str, Any]:
        """
        Get chatbot configuration by script token
        
        Args:
            script_token: Script token of the chatbot
            
        Returns:
            Chatbot configuration data
            
        Raises:
            ValueError: If chatbot not found or inactive
            Exception: If database operation fails
        """
        try:
            logger.info(f"Getting chatbot config for token: {script_token[:8]}...")
            
            if self.supabase_client:
                # Get chatbot with brand information
                result = self.supabase_client.table("chatbots").select(
                    "id, name, primary_color, secondary_color, animation_style, language, status, brands!inner(name, theme_color)"
                ).eq("script_token", script_token).execute()
                
                if not result.data:
                    raise ValueError("Chatbot not found")
                
                chatbot = result.data[0]
                
                if chatbot["status"] != "active":
                    raise ValueError("Chatbot is not active")
                
                # Format configuration for widget
                config = {
                    "chatbot": {
                        "id": chatbot["id"],
                        "name": chatbot["name"],
                        "primary_color": chatbot["primary_color"],
                        "secondary_color": chatbot["secondary_color"],
                        "animation_style": chatbot["animation_style"],
                        "language": chatbot["language"]
                    },
                    "brand": {
                        "name": chatbot["brands"]["name"],
                        "theme_color": chatbot["brands"]["theme_color"]
                    },
                    "script_token": script_token
                }
                
                logger.info(f"Chatbot config retrieved successfully: {chatbot['id']}")
                return config
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get chatbot config: {str(e)}")
            raise Exception(f"Failed to get chatbot config: {str(e)}")
    
    async def get_chatbot_stats(self, chatbot_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get chatbot statistics
        
        Args:
            chatbot_id: UUID of the chatbot
            user_id: ID of the user requesting stats
            
        Returns:
            Chatbot statistics
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Getting chatbot stats for {chatbot_id} by user {user_id}")
            
            # Validate chatbot permissions
            if not await self.validate_chatbot_permissions(user_id, chatbot_id):
                raise ValueError("User does not have permission to view this chatbot's stats")
            
            if self.supabase_client:
                # Get conversation count
                conversations = self.supabase_client.table("conversations").select("id", count="exact").eq("chatbot_id", chatbot_id).execute()
                conversation_count = conversations.count if conversations.count else 0
                
                # Get unique sessions count
                sessions = self.supabase_client.table("conversations").select("session_id").eq("chatbot_id", chatbot_id).execute()
                unique_sessions = len(set(session["session_id"] for session in sessions.data)) if sessions.data else 0
                
                # Get average latency
                latency_data = self.supabase_client.table("conversations").select("latency_ms").eq("chatbot_id", chatbot_id).execute()
                avg_latency = 0
                if latency_data.data:
                    latencies = [conv["latency_ms"] for conv in latency_data.data if conv["latency_ms"]]
                    avg_latency = sum(latencies) / len(latencies) if latencies else 0
                
                # Get feedback average
                feedback = self.supabase_client.table("feedback").select("rating, conversations!inner(chatbot_id)").eq("conversations.chatbot_id", chatbot_id).execute()
                avg_rating = 0
                if feedback.data:
                    ratings = [fb["rating"] for fb in feedback.data if fb["rating"]]
                    avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                stats = {
                    "total_conversations": conversation_count,
                    "unique_sessions": unique_sessions,
                    "average_latency_ms": round(avg_latency, 2),
                    "average_rating": round(avg_rating, 2),
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Chatbot stats retrieved successfully: {chatbot_id}")
                return stats
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get chatbot stats: {str(e)}")
            raise Exception(f"Failed to get chatbot stats: {str(e)}")
    
    async def validate_chatbot_permissions(self, user_id: str, chatbot_id: str) -> bool:
        """
        Validate if user has permission to access chatbot
        
        Args:
            user_id: ID of the user
            chatbot_id: UUID of the chatbot
            
        Returns:
            True if user has permission
        """
        try:
            if self.supabase_client:
                # Check if chatbot belongs to user through brand ownership
                result = self.supabase_client.table("chatbots").select(
                    "id, brands!inner(user_id)"
                ).eq("id", chatbot_id).eq("brands.user_id", user_id).execute()
                
                return bool(result.data)
            else:
                logger.warning("Supabase client not available for permission validation")
                return False
                
        except Exception as e:
            logger.error(f"Failed to validate chatbot permissions: {str(e)}")
            return False
    
    async def validate_brand_permissions(self, user_id: str, brand_id: str) -> bool:
        """
        Validate if user has permission to access brand
        
        Args:
            user_id: ID of the user
            brand_id: UUID of the brand
            
        Returns:
            True if user has permission
        """
        try:
            if self.supabase_client:
                result = self.supabase_client.table("brands").select("id").eq("id", brand_id).eq("user_id", user_id).execute()
                return bool(result.data)
            else:
                logger.warning("Supabase client not available for permission validation")
                return False
                
        except Exception as e:
            logger.error(f"Failed to validate brand permissions: {str(e)}")
            return False
    
    async def get_chatbot_by_id(self, chatbot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chatbot by ID
        
        Args:
            chatbot_id: UUID of the chatbot
            
        Returns:
            Chatbot data or None if not found
        """
        try:
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").select("*").eq("id", chatbot_id).execute()
                return result.data[0] if result.data else None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get chatbot by ID: {str(e)}")
            return None
    
    async def regenerate_script_token(self, chatbot_id: str, user_id: str) -> str:
        """
        Regenerate script token for chatbot
        
        Args:
            chatbot_id: UUID of the chatbot
            user_id: ID of the user
            
        Returns:
            New script token
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            logger.info(f"Regenerating script token for chatbot {chatbot_id} by user {user_id}")
            
            # Validate chatbot permissions
            if not await self.validate_chatbot_permissions(user_id, chatbot_id):
                raise ValueError("User does not have permission to regenerate token for this chatbot")
            
            # Generate new token
            new_token = self.generate_script_token()
            
            # Update in database
            if self.supabase_client:
                result = self.supabase_client.table("chatbots").update({
                    "script_token": new_token,
                    "token_regenerated_at": datetime.utcnow().isoformat()
                }).eq("id", chatbot_id).execute()
                
                if not result.data:
                    raise Exception("Failed to update script token")
                
                logger.info(f"Script token regenerated successfully for chatbot: {chatbot_id}")
                return new_token
            else:
                raise Exception("Supabase client not available")
                
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to regenerate script token: {str(e)}")
            raise Exception(f"Failed to regenerate script token: {str(e)}")