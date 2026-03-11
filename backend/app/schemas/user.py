"""
Pydantic Schemas - 用户相关
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ========== 用户 Schema ==========

class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """用户创建 Schema"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """用户更新 Schema"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    avatar: Optional[str] = None
    bio: Optional[str] = None
    subscription_plan: str
    subscription_expire_at: Optional[datetime] = None
    is_active: bool
    is_verified: bool
    total_replies: int
    today_replies: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    """用户详细信息响应"""
    plan_info: dict = {}
    accounts_count: int = 0
    rules_count: int = 0


# ========== 认证 Schema ==========

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(UserCreate):
    """注册请求"""
    invite_code: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr


# ========== 套餐 Schema ==========

class PlanInfo(BaseModel):
    """套餐信息"""
    plan: str
    name: str
    price: int
    accounts_limit: int
    daily_replies_limit: int
    keywords_limit: int
    features: dict


class SubscriptionResponse(BaseModel):
    """订阅信息响应"""
    plan: str
    plan_info: PlanInfo
    expire_at: Optional[datetime] = None
    auto_renew: bool
    status: str
    
    model_config = ConfigDict(from_attributes=True)