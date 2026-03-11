"""
数据模型 - 小红书账号模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class XHSAccount(Base):
    """小红书账号模型"""
    __tablename__ = "xhs_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    # 账号信息
    name: Mapped[str] = mapped_column(String(100), comment="账号名称/备注")
    
    # 登录凭证
    cookie_web_session: Mapped[Optional[str]] = mapped_column(Text)
    cookie_a1: Mapped[Optional[str]] = mapped_column(Text)
    
    # 账号信息
    xhs_user_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(100))
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    follower_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    # 监控配置
    monitor_comments: Mapped[bool] = mapped_column(Boolean, default=True)
    monitor_messages: Mapped[bool] = mapped_column(Boolean, default=False)
    monitor_note_ids: Mapped[Optional[str]] = mapped_column(Text, comment="指定笔记ID，多个用逗号分隔")
    ignored_users: Mapped[Optional[str]] = mapped_column(Text, comment="忽略用户ID，多个用逗号分隔")
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    login_status: Mapped[str] = mapped_column(String(20), default="unknown")  # unknown/valid/invalid/expired
    last_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cookie_expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    reply_rules: Mapped[list["ReplyRule"]] = relationship(
        "ReplyRule",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<XHSAccount(id={self.id}, name={self.name})>"


class ReplyRule(Base):
    """回复规则模型"""
    __tablename__ = "reply_rules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("xhs_accounts.id"), nullable=True)
    
    # 规则信息
    name: Mapped[str] = mapped_column(String(100))
    rule_type: Mapped[str] = mapped_column(String(20), comment="comment/private_message")
    match_type: Mapped[str] = mapped_column(String(20), default="fuzzy")  # exact/fuzzy/semantic
    
    # 关键词和回复
    keywords: Mapped[str] = mapped_column(Text, comment="关键词，多个用逗号分隔")
    reply_templates: Mapped[str] = mapped_column(Text, comment="回复模板，多个用换行符分隔")
    
    # 高级配置
    priority: Mapped[int] = mapped_column(Integer, default=1)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    use_ai_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text)
    
    # 统计
    match_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="reply_rules")
    account: Mapped[Optional["XHSAccount"]] = relationship("XHSAccount", back_populates="reply_rules")
    
    @property
    def keywords_list(self) -> list[str]:
        return [k.strip() for k in self.keywords.split(",") if k.strip()]
    
    @property
    def templates_list(self) -> list[str]:
        return [t.strip() for t in self.reply_templates.split("\n") if t.strip()]
    
    def __repr__(self):
        return f"<ReplyRule(id={self.id}, name={self.name})>"


class ReplyHistory(Base):
    """回复历史模型"""
    __tablename__ = "reply_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("xhs_accounts.id"))
    rule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reply_rules.id"), nullable=True)
    
    # 内容信息
    target_type: Mapped[str] = mapped_column(String(20))  # comment/private_message
    target_id: Mapped[str] = mapped_column(String(100), index=True)  # 评论ID/消息ID
    target_user_id: Mapped[Optional[str]] = mapped_column(String(100))
    target_content: Mapped[str] = mapped_column(Text)
    
    # 回复内容
    reply_content: Mapped[str] = mapped_column(Text)
    reply_status: Mapped[str] = mapped_column(String(20), default="success")  # success/failed/pending
    
    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="reply_history")
    
    def __repr__(self):
        return f"<ReplyHistory(id={self.id}, target_type={self.target_type})>"


class Subscription(Base):
    """订阅记录模型"""
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    # 订阅信息
    plan: Mapped[str] = mapped_column(String(20))  # free/pro/enterprise
    amount: Mapped[int] = mapped_column(Integer)  # 金额（分）
    currency: Mapped[str] = mapped_column(String(3), default="CNY")
    
    # 支付信息
    payment_method: Mapped[Optional[str]] = mapped_column(String(20))  # alipay/wechatpay
    payment_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
    # 时间信息
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/cancelled/expired
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, plan={self.plan}, status={self.status})>"