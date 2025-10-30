"""
Rate Limiting Middleware
API rate limiting ve abuse prevention
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter
    Production'da Redis kullanılması önerilir
    """

    def __init__(self):
        # {key: {timestamp: count}}
        self.requests: Dict[str, Dict[datetime, int]] = defaultdict(dict)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.utcnow()

    def _cleanup_old_entries(self):
        """Eski entry'leri temizle"""
        if datetime.utcnow() - self.last_cleanup < self.cleanup_interval:
            return

        current_time = datetime.utcnow()
        cleanup_threshold = current_time - timedelta(hours=1)

        for key in list(self.requests.keys()):
            self.requests[key] = {
                timestamp: count
                for timestamp, count in self.requests[key].items()
                if timestamp > cleanup_threshold
            }

            # Boş entry'leri sil
            if not self.requests[key]:
                del self.requests[key]

        self.last_cleanup = current_time

    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, Optional[int]]:
        """
        Rate limit kontrolü

        Args:
            key: Unique identifier (örn: user_id, IP address)
            max_requests: Maksimum istek sayısı
            window_seconds: Zaman penceresi (saniye)

        Returns:
            (is_limited, retry_after_seconds) tuple
        """
        self._cleanup_old_entries()

        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=window_seconds)

        # Bu zaman dilimindeki istekleri say
        request_count = sum(
            count for timestamp, count in self.requests[key].items()
            if timestamp > window_start
        )

        if request_count >= max_requests:
            # Rate limited
            # En eski isteğin ne zaman expire olacağını hesapla
            oldest_request = min(
                (timestamp for timestamp in self.requests[key].keys() if timestamp > window_start),
                default=current_time
            )
            retry_after = int((oldest_request + timedelta(seconds=window_seconds) - current_time).total_seconds())

            return True, max(retry_after, 1)

        # Rate limit'e takılmadı, isteği kaydet
        self.requests[key][current_time] = self.requests[key].get(current_time, 0) + 1

        return False, None


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """
    İstek yapan client'ın IP adresini al

    Args:
        request: FastAPI Request

    Returns:
        IP adresi
    """
    # X-Forwarded-For header'ını kontrol et (proxy/load balancer arkasında)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # İlk IP'yi al (client IP)
        return forwarded.split(",")[0].strip()

    # X-Real-IP header'ını kontrol et
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Direkt client host
    return request.client.host if request.client else "unknown"


async def rate_limit_by_ip(
    request: Request,
    max_requests: int = 100,
    window_seconds: int = 60
):
    """
    IP adresine göre rate limiting

    Args:
        request: FastAPI Request
        max_requests: Maksimum istek sayısı
        window_seconds: Zaman penceresi (saniye)

    Raises:
        HTTPException: Rate limit aşıldı
    """
    ip_address = get_client_ip(request)
    key = f"ip:{ip_address}"

    is_limited, retry_after = rate_limiter.is_rate_limited(
        key=key,
        max_requests=max_requests,
        window_seconds=window_seconds
    )

    if is_limited:
        logger.warning(f"Rate limit exceeded for IP: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Çok fazla istek. Lütfen {retry_after} saniye sonra tekrar deneyin.",
            headers={"Retry-After": str(retry_after)}
        )


async def rate_limit_by_user(
    request: Request,
    user_id: str,
    max_requests: int = 100,
    window_seconds: int = 60
):
    """
    Kullanıcı ID'ye göre rate limiting

    Args:
        request: FastAPI Request
        user_id: Kullanıcı ID
        max_requests: Maksimum istek sayısı
        window_seconds: Zaman penceresi (saniye)

    Raises:
        HTTPException: Rate limit aşıldı
    """
    key = f"user:{user_id}"

    is_limited, retry_after = rate_limiter.is_rate_limited(
        key=key,
        max_requests=max_requests,
        window_seconds=window_seconds
    )

    if is_limited:
        logger.warning(f"Rate limit exceeded for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Çok fazla istek. Lütfen {retry_after} saniye sonra tekrar deneyin.",
            headers={"Retry-After": str(retry_after)}
        )


async def rate_limit_auth_endpoints(request: Request):
    """
    Auth endpoint'leri için özel rate limiting
    (login, register, vb. için daha sıkı limitler)

    Args:
        request: FastAPI Request

    Raises:
        HTTPException: Rate limit aşıldı
    """
    ip_address = get_client_ip(request)
    key = f"auth:{ip_address}"

    # Auth endpoint'leri için daha sıkı limit
    is_limited, retry_after = rate_limiter.is_rate_limited(
        key=key,
        max_requests=10,  # 5 dakikada 10 istek
        window_seconds=300
    )

    if is_limited:
        logger.warning(f"Auth rate limit exceeded for IP: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Çok fazla authentication denemesi. Lütfen {retry_after} saniye sonra tekrar deneyin.",
            headers={"Retry-After": str(retry_after)}
        )


class RateLimitMiddleware:
    """
    Global rate limiting middleware

    Usage:
        app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    """

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # FastAPI Request oluştur
        from fastapi import Request
        request = Request(scope, receive)

        # Rate limit kontrolü
        ip_address = get_client_ip(request)
        key = f"global:{ip_address}"

        is_limited, retry_after = rate_limiter.is_rate_limited(
            key=key,
            max_requests=self.max_requests,
            window_seconds=self.window_seconds
        )

        if is_limited:
            # Rate limit aşıldı
            response_body = {
                "detail": f"Çok fazla istek. Lütfen {retry_after} saniye sonra tekrar deneyin."
            }

            import json
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"retry-after", str(retry_after).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps(response_body).encode(),
            })
            return

        # Rate limit'e takılmadı, devam et
        await self.app(scope, receive, send)
