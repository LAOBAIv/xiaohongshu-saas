"""
Pydantic Schemas - 账号和规则相关
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


# ========== 小红书账号 Schema ==========

class XHSAccountBase(BaseModel):
    """账号基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    cookie_web_session: Optional[str] = None
    cookie_a1: Optional[str] = None


class XHSAccountCreate(XHSAccountBase):
    """账号创建 Schema"""
    monitor_comments: bool = True
    monitor_messages: bool = False
    monitor_note_ids: Optional[str] = None
    ignored_users: Optional[str] = None


class XHSAccountUpdate(BaseModel):
    """账号更新 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    cookie_web_session: Optional[str] = None
    cookie_a1: Optional[str] = None
    monitor_comments: Optional[bool] = None
    monitor_messages: Optional[bool] = None
    monitor_note_ids: Optional[str] = None
    ignored_users: Optional[str] = None
    is_active: Optional[bool] = None


class XHSAccountResponse(XHSAccountBase):
    """账号响应 Schema"""
    id: int
    user_id: int
    xhs_user_id: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    follower_count: Optional[int] = None
    monitor_comments: bool
    monitor_messages: bool
    monitor_note_ids: Optional[str] = None
    ignored_users: Optional[str] = None
    is_active: bool
    login_status: str
    last_check_at: Optional[datetime] = None
    cookie_expire_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class XHSAccountStatusResponse(BaseModel):
    """账号状态响应"""
    id: int
    name: str
    login_status: str
    last_check_at: Optional[datetime] = None
    is_active: bool


class CookieRefreshRequest(BaseModel):
    """Cookie刷新请求"""
    cookie_web_session: str
    cookie_a1: str


# ========== 回复规则 Schema ==========

class ReplyRuleBase(BaseModel):
    """规则基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    rule_type: str = Field(..., pattern="^(comment|private_message)$")
    match_type: str = Field(default="fuzzy", pattern="^(exact|fuzzy|semantic)$")
    keywords: str = Field(..., description="关键词，多个用逗号分隔")
    reply_templates: str = Field(..., description="回复模板，多个用换行符分隔")


class ReplyRuleCreate(ReplyRuleBase):
    """规则创建 Schema"""
    account_id: Optional[int] = None
    priority: int = Field(default=1, ge=1, le=100)
    is_enabled: bool = True
    use_ai_reply: bool = False
    ai_prompt: Optional[str] = None


class ReplyRuleUpdate(BaseModel):
    """规则更新 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_type: Optional[str] = Field(None, pattern="^(comment|private_message)$")
    match_type: Optional[str] = Field(None, pattern="^(exact|fuzzy|semantic)$")
    keywords: Optional[str] = None
    reply_templates: Optional[str] = None
    account_id: Optional[int] = None
    priority: Optional[int] = Field(None, ge=1, le=100)
    is_enabled: Optional[bool] = None
    use_ai_reply: Optional[bool] = None
    ai_prompt: Optional[str] = None


class ReplyRuleResponse(ReplyRuleBase):
    """规则响应 Schema"""
    id: int
    user_id: int
    account_id: Optional[int] = None
    priority: int
    is_enabled: bool
    use_ai_reply: bool
    ai_prompt: Optional[str] = None
    match_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @property
    def keywords_list(self) -> List[str]:
        return [k.strip() for k in self.keywords.split(",") if k.strip()]
    
    @property
    def templates_list(self) -> List[str]:
        return [t.strip() for t in self.reply_templates.split("\n") if t.strip()]


# ========== 回复历史 Schema ==========

class ReplyHistoryResponse(BaseModel):
    """回复历史响应"""
    id: int
    account_id: int
    target_type: str
    target_id: str
    target_user_id: Optional[str] = None
    target_content: str
    reply_content: str
    reply_status: str
    error_message: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReplyHistoryListResponse(BaseModel):
    """回复历史列表响应"""
    items: List[ReplyHistoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ========== 统计 Schema ==========

class StatsOverview(BaseModel):
    """统计概览"""
    total_accounts: int
    active_accounts: int
    total_rules: int
    enabled_rules: int
    total_replies: int
    today_replies: int
    success_rate: float


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str
    replies: int
    success: int
    failed: int


class StatsTrendResponse(BaseModel):
    """统计趋势响应"""
    period: str  # 7d/30d/90d
    data: List[TrendDataPoint]


class StatsReplyResponse(BaseModel):
    """回复统计响应"""
    total: int
    today: int
    yesterday: int
    this_week: int
    this_month: int
    by_type: dict  # {"comment": xx, "private_message": xx}


# ========== 批量操作 Schema ==========

class BulkDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_items=1)


class BulkEnableRequest(BaseModel):
    """批量启用/禁用请求"""
    ids: List[int] = Field(..., min_items=1)
    enabled: bool