# MarkaMind Authentication & Security

## Genel Bakış

MarkaMind platformu, modern güvenlik standartlarına uygun çok katmanlı bir güvenlik mimarisi kullanır. Bu dokümantasyon JWT authentication, RBAC, rate limiting, API key management ve güvenlik best practices'lerini detaylandırır.

## 1. JWT (JSON Web Token) Implementation

### 1.1 JWT Architecture

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config.settings import settings

class JWTManager:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": str(uuid.uuid4())  # JWT ID for token revocation
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": str(uuid.uuid4())
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
```

### 1.2 Token Storage & Management

```python
# app/models/refresh_token.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    jti = Column(String(36), unique=True, nullable=False)  # JWT ID
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    # Device/session info for security
    device_info = Column(String(500))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    user = relationship("User", back_populates="refresh_tokens")

# Token blacklist for revoked tokens
class TokenBlacklist(BaseModel):
    __tablename__ = "token_blacklist"
    
    jti = Column(String(36), unique=True, nullable=False)
    token_type = Column(String(10), nullable=False)  # access, refresh
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String(100))  # logout, security_breach, expired
```

### 1.3 Token Refresh Strategy

```python
# app/api/v1/endpoints/auth.py
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    jwt_manager: JWTManager = Depends(get_jwt_manager)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token
    payload = jwt_manager.verify_token(refresh_request.refresh_token, "refresh")
    user_id = int(payload.get("sub"))
    jti = payload.get("jti")
    
    # Check if refresh token exists and is not revoked
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.jti == jti,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = jwt_manager.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

## 2. Role-Based Access Control (RBAC)

### 2.1 Role System Design

```python
# app/models/role.py
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, JSON, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    API_USER = "api_user"

class Permission(str, Enum):
    # User permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Chatbot permissions
    CHATBOT_READ = "chatbot:read"
    CHATBOT_WRITE = "chatbot:write"
    CHATBOT_DELETE = "chatbot:delete"
    CHATBOT_TRAIN = "chatbot:train"
    
    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_BILLING = "admin:billing"

# Role-Permission mapping table
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", back_populates="role")

class PermissionModel(BaseModel):
    __tablename__ = "permissions"
    
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    resource = Column(String(50), nullable=False)  # user, chatbot, analytics
    action = Column(String(50), nullable=False)    # read, write, delete
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
```

### 2.2 Permission Checking System

```python
# app/core/permissions.py
from typing import List, Set
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Permission, Role

class PermissionChecker:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for a user"""
        if not user.role:
            return set()
        
        permissions = set()
        for permission in user.role.permissions:
            permissions.add(permission.name)
        
        return permissions
    
    def has_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has specific permission"""
        if user.is_superuser:
            return True
        
        user_permissions = self.get_user_permissions(user)
        return required_permission in user_permissions
    
    def has_any_permission(self, user: User, required_permissions: List[str]) -> bool:
        """Check if user has any of the required permissions"""
        if user.is_superuser:
            return True
        
        user_permissions = self.get_user_permissions(user)
        return any(perm in user_permissions for perm in required_permissions)
    
    def has_all_permissions(self, user: User, required_permissions: List[str]) -> bool:
        """Check if user has all required permissions"""
        if user.is_superuser:
            return True
        
        user_permissions = self.get_user_permissions(user)
        return all(perm in user_permissions for perm in required_permissions)

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            db = kwargs.get('db')
            permission_checker = PermissionChecker(db)
            
            if not permission_checker.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[str]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            db = kwargs.get('db')
            permission_checker = PermissionChecker(db)
            
            if not permission_checker.has_any_permission(current_user, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required any of: {permissions}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 2.3 Resource-Level Permissions

```python
# app/core/resource_permissions.py
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.chatbot import Chatbot

class ResourcePermissionChecker:
    def __init__(self, db: Session):
        self.db = db
    
    def can_access_chatbot(self, user: User, chatbot_id: int, action: str = "read") -> bool:
        """Check if user can access specific chatbot"""
        chatbot = self.db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        
        if not chatbot:
            return False
        
        # Super admin can access everything
        if user.is_superuser:
            return True
        
        # Owner can access their own chatbots
        if chatbot.user_id == user.id:
            return True
        
        # Check role-based permissions for shared resources
        permission_name = f"chatbot:{action}"
        permission_checker = PermissionChecker(self.db)
        
        return permission_checker.has_permission(user, permission_name)
    
    def can_access_user_data(self, current_user: User, target_user_id: int) -> bool:
        """Check if user can access another user's data"""
        if current_user.is_superuser:
            return True
        
        # Users can access their own data
        if current_user.id == target_user_id:
            return True
        
        # Check admin permissions
        permission_checker = PermissionChecker(self.db)
        return permission_checker.has_permission(current_user, "admin:users")

def require_chatbot_access(action: str = "read"):
    """Decorator to check chatbot access permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            chatbot_id = kwargs.get('chatbot_id')
            db = kwargs.get('db')
            
            if not chatbot_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chatbot ID required"
                )
            
            resource_checker = ResourcePermissionChecker(db)
            
            if not resource_checker.can_access_chatbot(current_user, chatbot_id, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this chatbot"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 3. Rate Limiting Strategies

### 3.1 Redis-Based Rate Limiting

```python
# app/core/rate_limiting.py
import redis
import time
import hashlib
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from app.config.settings import settings

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_limits = {
            "anonymous": {"requests": 100, "window": 3600},  # 100 req/hour
            "authenticated": {"requests": 1000, "window": 3600},  # 1000 req/hour
            "premium": {"requests": 5000, "window": 3600},  # 5000 req/hour
            "api_key": {"requests": 10000, "window": 3600}  # 10000 req/hour
        }
    
    def get_client_id(self, request: Request, user_id: Optional[int] = None) -> str:
        """Generate unique client identifier"""
        if user_id:
            return f"user:{user_id}"
        
        # Use IP address for anonymous users
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def get_rate_limit_key(self, client_id: str, endpoint: str, window: int) -> str:
        """Generate Redis key for rate limiting"""
        timestamp = int(time.time() // window)
        return f"rate_limit:{client_id}:{endpoint}:{timestamp}"
    
    def check_rate_limit(
        self, 
        client_id: str, 
        endpoint: str, 
        limit: int, 
        window: int
    ) -> Dict[str, Any]:
        """Check if client is within rate limit"""
        key = self.get_rate_limit_key(client_id, endpoint, window)
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results = pipe.execute()
        
        current_requests = results[0]
        
        return {
            "allowed": current_requests <= limit,
            "current_requests": current_requests,
            "limit": limit,
            "window": window,
            "reset_time": int(time.time()) + window - (int(time.time()) % window)
        }
    
    def apply_rate_limit(
        self, 
        request: Request, 
        endpoint: str,
        user_id: Optional[int] = None,
        user_type: str = "anonymous"
    ):
        """Apply rate limiting to request"""
        client_id = self.get_client_id(request, user_id)
        limits = self.default_limits.get(user_type, self.default_limits["anonymous"])
        
        result = self.check_rate_limit(
            client_id, 
            endpoint, 
            limits["requests"], 
            limits["window"]
        )
        
        if not result["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": result["limit"],
                    "current": result["current_requests"],
                    "reset_time": result["reset_time"]
                },
                headers={
                    "X-RateLimit-Limit": str(result["limit"]),
                    "X-RateLimit-Remaining": str(max(0, result["limit"] - result["current_requests"])),
                    "X-RateLimit-Reset": str(result["reset_time"])
                }
            )

# Rate limiting middleware
class RateLimitMiddleware:
    def __init__(self, app, redis_client: redis.Redis):
        self.app = app
        self.rate_limiter = RateLimiter(redis_client)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip rate limiting for health checks
            if request.url.path in ["/health", "/docs", "/openapi.json"]:
                await self.app(scope, receive, send)
                return
            
            # Apply rate limiting
            try:
                # Determine user type based on authentication
                user_type = "anonymous"
                user_id = None
                
                # Check for API key in headers
                api_key = request.headers.get("X-API-Key")
                if api_key:
                    user_type = "api_key"
                    # Extract user_id from API key validation
                
                # Check for JWT token
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    user_type = "authenticated"
                    # Extract user_id from JWT token
                
                self.rate_limiter.apply_rate_limit(
                    request, 
                    request.url.path, 
                    user_id, 
                    user_type
                )
                
            except HTTPException as e:
                response = JSONResponse(
                    status_code=e.status_code,
                    content=e.detail,
                    headers=e.headers
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
```

### 3.2 Endpoint-Specific Rate Limits

```python
# app/core/endpoint_limits.py
ENDPOINT_RATE_LIMITS = {
    # Authentication endpoints
    "/api/v1/auth/login": {
        "anonymous": {"requests": 5, "window": 300},  # 5 attempts per 5 min
        "authenticated": {"requests": 10, "window": 300}
    },
    "/api/v1/auth/register": {
        "anonymous": {"requests": 3, "window": 3600},  # 3 registrations per hour
    },
    "/api/v1/auth/forgot-password": {
        "anonymous": {"requests": 3, "window": 3600},
    },
    
    # Chat endpoints (high frequency)
    "/api/v1/chat/*/message": {
        "authenticated": {"requests": 100, "window": 60},  # 100 messages per minute
        "premium": {"requests": 500, "window": 60},
        "api_key": {"requests": 1000, "window": 60}
    },
    
    # Training endpoints (resource intensive)
    "/api/v1/chatbots/*/train/*": {
        "authenticated": {"requests": 10, "window": 3600},  # 10 training ops per hour
        "premium": {"requests": 50, "window": 3600}
    },
    
    # File upload endpoints
    "/api/v1/files/upload": {
        "authenticated": {"requests": 20, "window": 3600},  # 20 uploads per hour
        "premium": {"requests": 100, "window": 3600}
    },
    
    # Analytics endpoints
    "/api/v1/analytics/*": {
        "authenticated": {"requests": 100, "window": 3600},
        "premium": {"requests": 500, "window": 3600}
    }
}

def get_endpoint_limit(endpoint: str, user_type: str) -> Dict[str, int]:
    """Get rate limit for specific endpoint and user type"""
    # Find matching endpoint pattern
    for pattern, limits in ENDPOINT_RATE_LIMITS.items():
        if pattern.replace("*", ".*") in endpoint:
            return limits.get(user_type, {"requests": 100, "window": 3600})
    
    # Default limits
    default_limits = {
        "anonymous": {"requests": 100, "window": 3600},
        "authenticated": {"requests": 1000, "window": 3600},
        "premium": {"requests": 5000, "window": 3600},
        "api_key": {"requests": 10000, "window": 3600}
    }
    
    return default_limits.get(user_type, default_limits["anonymous"])
```

## 4. Security Best Practices

### 4.1 Input Validation & Sanitization

```python
# app/core/validation.py
import re
import html
from typing import Any, Dict
from pydantic import validator, BaseModel
from fastapi import HTTPException, status

class SecurityValidator:
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate and sanitize email address"""
        email = email.lower().strip()
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
        
        return password
    
    @staticmethod
    def sanitize_html_input(text: str) -> str:
        """Sanitize HTML input to prevent XSS"""
        if not text:
            return text
        
        # HTML escape
        text = html.escape(text)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?</iframe>',
            r'<object.*?</object>',
            r'<embed.*?</embed>'
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text
    
    @staticmethod
    def validate_file_upload(filename: str, content_type: str, max_size: int) -> bool:
        """Validate file upload security"""
        # Check file extension
        allowed_extensions = {'.pdf', '.txt', '.docx', '.md', '.png', '.jpg', '.jpeg', '.gif'}
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if f'.{file_ext}' not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )
        
        # Check content type
        allowed_content_types = {
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/markdown',
            'image/png',
            'image/jpeg',
            'image/gif'
        }
        
        if content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content type not allowed"
            )
        
        return True

# Pydantic models with security validation
class SecureUserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        return SecurityValidator.validate_email(v)
    
    @validator('password')
    def validate_password(cls, v):
        return SecurityValidator.validate_password(v)
    
    @validator('first_name', 'last_name', 'company_name')
    def sanitize_text_fields(cls, v):
        if v:
            return SecurityValidator.sanitize_html_input(v)
        return v
```

### 4.2 SQL Injection Prevention

```python
# app/core/database_security.py
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Any, Dict, List

class SecureQueryBuilder:
    
    @staticmethod
    def safe_query_with_params(
        db: Session, 
        query_template: str, 
        params: Dict[str, Any]
    ) -> List[Any]:
        """Execute parameterized query safely"""
        # Use SQLAlchemy's text() with bound parameters
        query = text(query_template)
        result = db.execute(query, params)
        return result.fetchall()
    
    @staticmethod
    def validate_order_by(order_by: str, allowed_columns: List[str]) -> str:
        """Validate ORDER BY clause to prevent SQL injection"""
        if not order_by:
            return "id"
        
        # Remove whitespace and convert to lowercase
        order_by = order_by.strip().lower()
        
        # Check if it's in allowed columns
        column = order_by.replace(' desc', '').replace(' asc', '')
        if column not in [col.lower() for col in allowed_columns]:
            raise ValueError(f"Invalid order by column: {column}")
        
        return order_by
    
    @staticmethod
    def build_search_query(
        base_query: str,
        search_term: str,
        search_columns: List[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Build safe search query with LIKE conditions"""
        if not search_term or not search_columns:
            return base_query, {}
        
        # Escape special characters for LIKE
        search_term = search_term.replace('%', '\\%').replace('_', '\\_')
        search_term = f"%{search_term}%"
        
        # Build WHERE conditions
        conditions = []
        params = {}
        
        for i, column in enumerate(search_columns):
            param_name = f"search_term_{i}"
            conditions.append(f"{column} ILIKE :{param_name}")
            params[param_name] = search_term
        
        where_clause = " OR ".join(conditions)
        query = f"{base_query} WHERE ({where_clause})"
        
        return query, params
```

### 4.3 HTTPS & TLS Configuration

```python
# app/core/tls_config.py
import ssl
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def configure_tls_security(app: FastAPI):
    """Configure TLS and HTTPS security"""
    
    # Force HTTPS redirect in production
    if settings.ENVIRONMENT == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted host middleware
    allowed_hosts = settings.ALLOWED_HOSTS.split(",") if settings.ALLOWED_HOSTS else ["*"]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        
        return response

# SSL Context for production
def create_ssl_context():
    """Create SSL context with security best practices"""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Load certificate files
    context.load_cert_chain(
        settings.SSL_CERT_PATH,
        settings.SSL_KEY_PATH
    )
    
    # Security settings
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
    
    return context
```

## 5. API Key Management

### 5.1 API Key Generation & Storage

```python
# app/services/api_key_service.py
import secrets
import hashlib
import hmac
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.api_key import APIKey
from app.models.user import User

class APIKeyService:
    def __init__(self, db: Session):
        self.db = db
        self.key_prefix = "mm_"  # MarkaMind prefix
        self.key_length = 32
    
    def generate_api_key(self) -> tuple[str, str]:
        """Generate API key and its hash"""
        # Generate random key
        key_bytes = secrets.token_bytes(self.key_length)
        key = secrets.token_urlsafe(self.key_length)
        
        # Create full key with prefix
        full_key = f"{self.key_prefix}{key}"
        
        # Create hash for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        return full_key, key_hash
    
    def create_api_key(
        self,
        user_id: int,
        name: str,
        permissions: List[str],
        rate_limit: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        allowed_ips: Optional[List[str]] = None
    ) -> tuple[APIKey, str]:
        """Create new API key"""
        
        # Generate key and hash
        api_key, key_hash = self.generate_api_key()
        
        # Get key prefix for identification
        key_prefix = api_key[:8]  # First 8 characters for display
        
        # Create API key record
        db_api_key = APIKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=permissions,
            rate_limit=rate_limit or 1000,
            expires_at=expires_at,
            allowed_ips=allowed_ips or []
        )
        
        self.db.add(db_api_key)
        self.db.commit()
        self.db.refresh(db_api_key)
        
        return db_api_key, api_key
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return associated record"""
        if not api_key.startswith(self.key_prefix):
            return None
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Find matching API key
        db_api_key = self.db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        ).first()
        
        if not db_api_key:
            return None
        
        # Check expiration
        if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used timestamp
        db_api_key.last_used = datetime.utcnow()
        db_api_key.usage_count += 1
        self.db.commit()
        
        return db_api_key
    
    def check_api_key_permissions(
        self, 
        api_key: APIKey, 
        required_permission: str,
        client_ip: Optional[str] = None
    ) -> bool:
        """Check if API key has required permissions"""
        
        # Check IP restrictions
        if api_key.allowed_ips and client_ip:
            if client_ip not in api_key.allowed_ips:
                return False
        
        # Check permissions
        if required_permission not in api_key.permissions:
            return False
        
        return True
    
    def revoke_api_key(self, api_key_id: int, user_id: int) -> bool:
        """Revoke API key"""
        api_key = self.db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()
        
        if not api_key:
            return False
        
        api_key.is_active = False
        self.db.commit()
        
        return True
```

### 5.2 API Key Authentication Dependency

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.services.api_key_service import APIKeyService
from app.models.api_key import APIKey
from app.models.user import User

security = HTTPBearer(auto_error=False)

async def get_api_key_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[tuple[User, APIKey]]:
    """Get user from API key authentication"""
    
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        # Try Authorization header
        if credentials:
            api_key = credentials.credentials
        else:
            return None
    
    if not api_key:
        return None
    
    # Validate API key
    api_key_service = APIKeyService(db)
    db_api_key = api_key_service.validate_api_key(api_key)
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Get associated user
    user = db.query(User).filter(
        User.id == db_api_key.user_id,
        User.is_active == True
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with API key not found"
        )
    
    # Check IP restrictions
    client_ip = request.client.host
    if db_api_key.allowed_ips and client_ip not in db_api_key.allowed_ips:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key not authorized for this IP address"
        )
    
    return user, db_api_key

def require_api_key_permission(permission: str):
    """Decorator to require specific API key permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            api_key_user = kwargs.get('api_key_user')
            if not api_key_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key authentication required"
                )
            
            user, api_key = api_key_user
            
            if permission not in api_key.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"API key missing required permission: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 5.3 API Key Management Endpoints

```python
# app/api/v1/endpoints/api_keys.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user, get_db
from app.services.api_key_service import APIKeyService
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyList
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new API key"""
    service = APIKeyService(db)
    
    db_api_key, api_key = service.create_api_key(
        user_id=current_user.id,
        name=api_key_data.name,
        permissions=api_key_data.permissions,
        rate_limit=api_key_data.rate_limit,
        expires_at=api_key_data.expires_at,
        allowed_ips=api_key_data.allowed_ips
    )
    
    return APIKeyResponse(
        id=db_api_key.id,
        name=db_api_key.name,
        key=api_key,  # Only returned once!
        key_prefix=db_api_key.key_prefix,
        permissions=db_api_key.permissions,
        rate_limit=db_api_key.rate_limit,
        expires_at=db_api_key.expires_at,
        created_at=db_api_key.created_at
    )

@router.get("/", response_model=List[APIKeyList])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's API keys"""
    api_keys = db.query(APIKey).filter(
        APIKey.user_id == current_user.id,
        APIKey.is_active == True
    ).all()
    
    return [
        APIKeyList(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            permissions=key.permissions,
            last_used=key.last_used,
            usage_count=key.usage_count,
            created_at=key.created_at
        )
        for key in api_keys
    ]

@router.delete("/{api_key_id}")
async def revoke_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke API key"""
    service = APIKeyService(db)
    
    if not service.revoke_api_key(api_key_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key revoked successfully"}
```

## 6. Security Monitoring & Logging

### 6.1 Security Event Logging

```python
# app/core/security_logger.py
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.security_log import SecurityLog

class SecurityLogger:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("security")
    
    def log_authentication_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        failure_reason: Optional[str] = None
    ):
        """Log authentication attempts"""
        event_data = {
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "failure_reason": failure_reason
        }
        
        self._log_security_event("authentication_attempt", event_data)
    
    def log_permission_denied(
        self,
        user_id: int,
        resource: str,
        action: str,
        ip_address: str
    ):
        """Log permission denied events"""
        event_data = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip_address
        }
        
        self._log_security_event("permission_denied", event_data)
    
    def log_suspicious_activity(
        self,
        user_id: Optional[int],
        activity_type: str,
        details: Dict[str, Any],
        ip_address: str
    ):
        """Log suspicious activities"""
        event_data = {
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details,
            "ip_address": ip_address
        }
        
        self._log_security_event("suspicious_activity", event_data)
    
    def _log_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """Internal method to log security events"""
        # Log to database
        security_log = SecurityLog(
            event_type=event_type,
            event_data=event_data,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(security_log)
        self.db.commit()
        
        # Log to application logger
        self.logger.warning(
            f"Security Event: {event_type}",
            extra={"event_data": event_data}
        )
```

### 6.2 Brute Force Protection

```python
# app/core/brute_force_protection.py
from typing import Dict
import time
from app.core.rate_limiting import RateLimiter

class BruteForceProtection:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.attempt_window = 300    # 5 minutes
    
    def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is locked out"""
        lockout_key = f"lockout:{identifier}"
        return self.redis.exists(lockout_key)
    
    def record_failed_attempt(self, identifier: str) -> Dict[str, Any]:
        """Record failed authentication attempt"""
        attempts_key = f"attempts:{identifier}"
        lockout_key = f"lockout:{identifier}"
        
        # Increment attempts
        attempts = self.redis.incr(attempts_key)
        
        # Set expiration on first attempt
        if attempts == 1:
            self.redis.expire(attempts_key, self.attempt_window)
        
        # Check if max attempts reached
        if attempts >= self.max_attempts:
            # Lock out the identifier
            self.redis.setex(lockout_key, self.lockout_duration, "locked")
            self.redis.delete(attempts_key)
            
            return {
                "locked_out": True,
                "attempts": attempts,
                "lockout_duration": self.lockout_duration
            }
        
        return {
            "locked_out": False,
            "attempts": attempts,
            "max_attempts": self.max_attempts
        }
    
    def clear_attempts(self, identifier: str):
        """Clear failed attempts for identifier"""
        attempts_key = f"attempts:{identifier}"
        self.redis.delete(attempts_key)
```

Bu authentication ve security sistemi, MarkaMind platformunu modern güvenlik tehditlerine karşı koruyacak kapsamlı bir güvenlik altyapısı sağlar.