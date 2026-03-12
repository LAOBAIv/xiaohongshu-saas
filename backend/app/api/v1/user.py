"""
用户API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    SubscriptionResponse,
    PlanInfo
)
from app.core.config import SUBSCRIPTION_PLANS

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: CurrentUser,
    db: DbSession
):
    """获取用户资料"""
    # 统计账号和规则数量
    from app.models.db_models import XHSAccount, ReplyRule
    
    accounts_result = db.execute(
        select(XHSAccount).where(XHSAccount.user_id == current_user.id)
    )
    accounts = accounts_result.scalars().all()
    
    rules_result = db.execute(
        select(ReplyRule).where(ReplyRule.user_id == current_user.id)
    )
    rules = rules_result.scalars().all()
    
    user_data = UserResponse.model_validate(current_user)
    user_dict = user_data.model_dump()
    
    # 添加额外信息
    user_dict["plan_info"] = SUBSCRIPTION_PLANS.get(current_user.subscription_plan, SUBSCRIPTION_PLANS["free"])
    user_dict["accounts_count"] = len(accounts)
    user_dict["rules_count"] = len(rules)
    
    return UserProfileResponse(**user_dict)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: UserUpdate,
    current_user: CurrentUser,
    db: DbSession
):
    """更新用户资料"""
    update_data = request.model_dump(exclude_unset=True)
    
    # 检查邮箱是否已被使用
    if "email" in update_data and update_data["email"]:
        result = db.execute(
            select(User).where(
                User.email == update_data["email"],
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    current_user: CurrentUser
):
    """获取订阅信息"""
    plan_info = SUBSCRIPTION_PLANS.get(current_user.subscription_plan, SUBSCRIPTION_PLANS["free"])
    
    return SubscriptionResponse(
        plan=current_user.subscription_plan,
        plan_info=PlanInfo(
            plan=current_user.subscription_plan,
            name=plan_info["name"],
            price=plan_info["price"],
            accounts_limit=plan_info["accounts_limit"],
            daily_replies_limit=plan_info["daily_replies_limit"],
            keywords_limit=plan_info["keywords_limit"],
            features=plan_info["features"]
        ),
        expire_at=current_user.subscription_expire_at,
        auto_renew=current_user.subscription_auto_renew,
        status="active" if current_user.subscription_expire_at and current_user.subscription_expire_at > datetime.utcnow() else "expired"
    )


# 需要导入datetime
from datetime import datetime