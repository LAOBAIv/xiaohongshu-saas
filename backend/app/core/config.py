from pydantic_settings import BaseSettings
from typing import List
import os

# 订阅套餐配置
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "免费版",
        "price": 0,
        "accounts_limit": 1,
        "daily_replies_limit": 50,
        "keywords_limit": 5,
        "features": {
            "auto_reply": True,
            "ai_reply": False,
            "analytics": False,
            "priority_support": False,
        }
    },
    "pro": {
        "name": "专业版",
        "price": 29.9,
        "accounts_limit": 5,
        "daily_replies_limit": 500,
        "keywords_limit": 50,
        "features": {
            "auto_reply": True,
            "ai_reply": True,
            "analytics": True,
            "priority_support": False,
        }
    },
    "enterprise": {
        "name": "企业版",
        "price": 99.9,
        "accounts_limit": -1,
        "daily_replies_limit": -1,
        "keywords_limit": -1,
        "features": {
            "auto_reply": True,
            "ai_reply": True,
            "analytics": True,
            "priority_support": True,
        }
    }
}

class Settings(BaseSettings):
    # 环境标识
    ENV: str = "development"  # development / production
    
    API_V1_STR: str = "/api/v1"
    APP_NAME: str = "小红书SAAS API"
    APP_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "小红书SAAS API"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # JWT配置 - 生产环境请使用强随机密钥
    SECRET_KEY: str = "25caf5c3a7fc3d370d5220fd4d1e3339943f567cb3f972ce0fb1667510ece3a0"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - 生产环境请限定域名
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 生产环境自动调整
        if os.getenv("ENV") == "production" or self.ENV == "production":
            self.DEBUG = False
            self.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
            self.CORS_ORIGINS = self.ALLOWED_ORIGINS

settings = Settings()