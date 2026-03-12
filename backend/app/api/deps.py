"""
API依赖注入
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, SessionLocal
from app.core.security import decode_token
from app.models.user import User

# 安全认证
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return user


def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)] = None,
    db: Annotated[Session, Depends(get_db)] = None
) -> Optional[User]:
    """获取可选用户（未登录返回None）"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


# 类型别名
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


# ========== 账号权限检查 ==========

def get_user_account(
    account_id: Annotated[int, Path(ge=1)],
    user: CurrentUser,
    db: DbSession
) -> "XHSAccount":
    """获取用户的账号（带权限检查）"""
    from app.models.db_models import XHSAccount
    from sqlalchemy import and_
    
    result = db.execute(
        select(XHSAccount).where(
            and_(
                XHSAccount.id == account_id,
                XHSAccount.user_id == user.id
            )
        )
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在或无权限",
        )
    
    return account


def get_user_rule(
    rule_id: Annotated[int, Path(ge=1)],
    user: CurrentUser,
    db: DbSession
) -> "ReplyRule":
    """获取用户的规则（带权限检查）"""
    from app.models.db_models import ReplyRule
    from sqlalchemy import and_
    
    result = db.execute(
        select(ReplyRule).where(
            and_(
                ReplyRule.id == rule_id,
                ReplyRule.user_id == user.id
            )
        )
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在或无权限",
        )
    
    return rule


# 导入需要前向声明的类型
from app.models.db_models import XHSAccount, ReplyRule