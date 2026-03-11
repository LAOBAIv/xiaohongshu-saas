"""
认证API路由
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token
)
from app.models.user import User
from app.schemas.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshTokenRequest,
    UserResponse
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    db: DbSession
):
    """用户注册"""
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if request.email:
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 创建用户
    user = User(
        username=request.username,
        email=request.email,
        phone=request.phone,
        nickname=request.nickname or request.username,
        password_hash=get_password_hash(request.password),
        subscription_plan="free",  # 默认免费版
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 生成Token
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: DbSession
):
    """用户登录"""
    # 查找用户（支持用户名或邮箱）
    result = await db.execute(
        select(User).where(
            (User.username == request.username) | 
            (User.email == request.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 生成Token
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DbSession
):
    """刷新Token"""
    payload = verify_token(request.refresh_token, "refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新Token无效或已过期"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 生成新Token
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(current_user: CurrentUser):
    """退出登录"""
    # 在实际应用中，可以将token加入黑名单
    return {"message": "退出成功"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DbSession
):
    """修改密码"""
    user = current_user
    
    # 验证旧密码
    if not verify_password(request.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(request.new_password)
    await db.commit()
    
    return {"message": "密码修改成功"}


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: DbSession
):
    """忘记密码（发送重置邮件）"""
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # 为了安全起见，不暴露用户是否存在
        return {"message": "如果邮箱存在，已发送重置链接"}
    
    # TODO: 发送重置邮件
    
    return {"message": "如果邮箱存在，已发送重置链接"}