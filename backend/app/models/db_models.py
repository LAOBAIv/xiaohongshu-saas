"""
数据库模型 - 小红书相关
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class LoginStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"


class XHSAccount(Base):
    """小红书账号模型"""
    __tablename__ = "xhs_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 账号信息
    name = Column(String(100), nullable=False)
    xhs_id = Column(String(100), nullable=True)
    
    # Cookie
    cookie_web_session = Column(Text, nullable=True)
    cookie_a1 = Column(Text, nullable=True)
    
    # 监控设置
    monitor_comments = Column(Boolean, default=True)
    monitor_messages = Column(Boolean, default=False)
    monitor_note_ids = Column(JSON, default=list)
    ignored_users = Column(JSON, default=list)
    
    # 状态
    login_status = Column(String(20), default=LoginStatus.UNKNOWN.value)
    is_active = Column(Boolean, default=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="accounts")
    rules = relationship("ReplyRule", back_populates="account", cascade="all, delete-orphan")
    reply_history = relationship("ReplyHistory", back_populates="account", cascade="all, delete-orphan")


class ReplyRule(Base):
    """回复规则模型"""
    __tablename__ = "reply_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("xhs_accounts.id"), nullable=True)
    
    # 规则信息
    name = Column(String(100), nullable=False)
    rule_type = Column(String(20), default="keyword")  # keyword, ai, random
    keywords = Column(JSON, default=list)  # 关键词列表
    reply_content = Column(Text, nullable=False)  # 回复内容
    ai_prompt = Column(Text, nullable=True)  # AI回复提示词
    
    # 设置
    match_type = Column(String(20), default="exact")  # exact, fuzzy, regex
    priority = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
    reply_delay = Column(Integer, default=0)  # 回复延迟（秒）
    
    # 统计
    match_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="reply_rules")
    account = relationship("XHSAccount", back_populates="rules", foreign_keys="ReplyRule.account_id")


class ReplyHistory(Base):
    """回复历史模型"""
    __tablename__ = "reply_history"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("xhs_accounts.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("reply_rules.id"), nullable=True)
    
    # 评论信息
    comment_id = Column(String(100), nullable=True)
    note_id = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    
    # 回复信息
    reply_content = Column(Text, nullable=False)
    reply_status = Column(String(20), default="pending")  # pending, success, failed
    reply_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    account = relationship("XHSAccount", back_populates="reply_history")
    rule = relationship("ReplyRule")
    user = relationship("User", back_populates="reply_history")


class SubscriptionOrder(Base):
    """订阅订单模型"""
    __tablename__ = "subscription_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 订单信息
    order_no = Column(String(64), unique=True, index=True)
    amount = Column(Float, default=0)
    tier = Column(String(20), nullable=False)
    duration_days = Column(Integer, default=30)
    
    # 支付信息
    payment_method = Column(String(20), nullable=True)  # wechat, alipay
    payment_status = Column(String(20), default="pending")  # pending, paid, failed
    paid_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)