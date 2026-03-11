"""
应用配置模块
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "小红书自动回复 SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/xhs_saas",
        description="数据库连接地址"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS 配置
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # 邮件配置 (可选)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM: Optional[str] = None
    
    # 支付配置 (可选)
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None
    WECHATPAY_MCHID: Optional[str] = None
    WECHATPAY_PRIVATE_KEY: Optional[str] = None
    
    # 小红书爬虫配置
    XHS_REQUEST_TIMEOUT: int = 30
    XHS_MAX_RETRIES: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()


# 套餐配置
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "免费版",
        "price": 0,
        "accounts_limit": 1,
        "daily_replies_limit": 50,
        "keywords_limit": 5,
        "features": {
            "comment_monitor": True,
            "private_message_monitor": False,
            "ai_reply": False,
            "api_access": False,
            "export_data": False,
            "priority_support": False,
        }
    },
    "pro": {
        "name": "专业版",
        "price": 99,
        "accounts_limit": 5,
        "daily_replies_limit": 500,
        "keywords_limit": 50,
        "features": {
            "comment_monitor": True,
            "private_message_monitor": True,
            "ai_reply": True,
            "api_access": True,
            "export_data": True,
            "priority_support": False,
        }
    },
    "enterprise": {
        "name": "企业版",
        "price": 299,
        "accounts_limit": -1,  # 无限
        "daily_replies_limit": -1,
        "keywords_limit": -1,
        "features": {
            "comment_monitor": True,
            "private_message_monitor": True,
            "ai_reply": True,
            "api_access": True,
            "export_data": True,
            "priority_support": True,
        }
    }
}