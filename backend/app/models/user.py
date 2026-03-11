"""
数据模型 - 用户模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 账号信息
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # 用户信息
    nickname: Mapped[Optional[str]] = mapped_column(String(100))
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    
    # 会员信息
    subscription_plan: Mapped[str] = mapped_column(String(20), default="free")  # free/pro/enterprise
    subscription_expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    subscription_auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 第三方登录
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(20))
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # 使用量统计
    total_replies: Mapped[int] = mapped_column(Integer, default=0)
    today_replies: Mapped[int] = mapped_column(Integer, default=0)
    replies_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 关系
    accounts: Mapped[list["XHSAccount"]] = relationship(
        "XHSAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reply_rules: Mapped[list["ReplyRule"]] = relationship(
        "ReplyRule",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reply_history: Mapped[list["ReplyHistory"]] = relationship(
        "ReplyHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
    
    @property
    def plan_info(self) -> dict:
        """获取套餐信息"""
        from app.core.config import SUBSCRIPTION_PLANS
        return SUBSCRIPTION_PLANS.get(self.subscription_plan, SUBSCRIPTION_PLANS["free"])
    
    def can_use_feature(self, feature: str) -> bool:
        """检查是否可以使用某个功能"""
        plan = self.plan_info
        return plan["features"].get(feature, False)
    
    def check_limits(self, limit_type: str, value: int = 1) -> bool:
        """检查是否达到限制"""
        plan = self.plan_info
        
        if limit_type == "accounts":
            limit = plan["accounts_limit"]
            if limit == -1:
                return True
            current = len(self.accounts)
            return current + value <= limit
        
        elif limit_type == "daily_replies":
            limit = plan["daily_replies_limit"]
            if limit == -1:
                return True
            # 重置每日计数
            if self.replies_reset_at and self.replies_reset_at.date() < datetime.utcnow().date():
                self.today_replies = 0
                self.replies_reset_at = datetime.utcnow()
            return self.today_replies + value <= limit
        
        elif limit_type == "keywords":
            limit = plan["keywords_limit"]
            if limit == -1:
                return True
            current = len(self.reply_rules)
            return current + value <= limit
        
        return True