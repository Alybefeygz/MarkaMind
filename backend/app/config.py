from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str
    supabase_api_key: str
    supabase_anon_key: str
    supabase_project_ref: str
    supabase_jwt_secret: str

    # Database Password
    password: str

    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Configuration
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "meta-llama/llama-3.1-8b-instruct:free"

    # Storage Configuration
    brand_logo_bucket: str = "brand-logos"
    brand_logo_base_url: Optional[str] = None

    # Properties for backward compatibility (uppercase access)
    @property
    def SUPABASE_URL(self) -> str:
        return self.supabase_url

    @property
    def SUPABASE_API_KEY(self) -> str:
        return self.supabase_api_key

    @property
    def SUPABASE_ANON_KEY(self) -> str:
        return self.supabase_anon_key

    @property
    def SUPABASE_JWT_SECRET(self) -> str:
        return self.supabase_jwt_secret

    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key

    @property
    def ALGORITHM(self) -> str:
        return self.algorithm

    @property
    def DEBUG(self) -> bool:
        return self.debug

    @property
    def HOST(self) -> str:
        return self.host

    @property
    def PORT(self) -> int:
        return self.port

    @property
    def OPENROUTER_API_KEY(self) -> Optional[str]:
        return self.openrouter_api_key

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()