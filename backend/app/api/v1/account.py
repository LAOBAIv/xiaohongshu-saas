"""
账号管理API路由
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession, get_user_account
from app.models.db_models import XHSAccount, ReplyRule
from app.schemas.account import (
    XHSAccountCreate,
    XHSAccountResponse,
    XHSAccountStatusResponse,
    XHSAccountUpdate,
    ReplyRuleCreate,
    ReplyRuleResponse,
    ReplyRuleUpdate,
    ReplyHistoryListResponse,
    ReplyHistoryResponse,
    StatsOverview,
    StatsTrendResponse,
    StatsReplyResponse,
    TrendDataPoint,
    BulkDeleteRequest,
    BulkEnableRequest
)

router = APIRouter(prefix="/accounts", tags=["账号管理"])


# ========== 账号接口 ==========

@router.get("", response_model=List[XHSAccountResponse])
async def get_accounts(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None
):
    """获取账号列表"""
    query = select(XHSAccount).where(XHSAccount.user_id == current_user.id)
    
    if is_active is not None:
        query = query.where(XHSAccount.is_active == is_active)
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    accounts = result.scalars().all()
    
    return [XHSAccountResponse.model_validate(a) for a in accounts]


@router.get("/stats", response_model=dict)
async def get_accounts_stats(
    current_user: CurrentUser,
    db: DbSession
):
    """获取账号统计"""
    # 统计账号数量
    result = await db.execute(
        select(
            func.count(XHSAccount.id).label("total"),
            func.sum(func.cast(XHSAccount.is_active, int)).label("active")
        ).where(XHSAccount.user_id == current_user.id)
    )
    row = result.one()
    
    return {
        "total": row.total or 0,
        "active": row.active or 0
    }


@router.post("", response_model=XHSAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: XHSAccountCreate,
    current_user: CurrentUser,
    db: DbSession
):
    """添加账号"""
    # 检查账号数量限制
    if not current_user.check_limits("accounts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="已达到账号数量上限，请升级套餐"
        )
    
    account = XHSAccount(
        user_id=current_user.id,
        name=request.name,
        cookie_web_session=request.cookie_web_session,
        cookie_a1=request.cookie_a1,
        monitor_comments=request.monitor_comments,
        monitor_messages=request.monitor_messages,
        monitor_note_ids=request.monitor_note_ids,
        ignored_users=request.ignored_users,
        login_status="valid" if (request.cookie_web_session and request.cookie_a1) else "unknown"
    )
    
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    return XHSAccountResponse.model_validate(account)


@router.get("/{account_id}", response_model=XHSAccountResponse)
async def get_account(
    account: XHSAccount = Depends(get_user_account)
):
    """获取账号详情"""
    return XHSAccountResponse.model_validate(account)


@router.put("/{account_id}", response_model=XHSAccountResponse)
async def update_account(
    request: XHSAccountUpdate,
    account: XHSAccount = Depends(get_user_account),
    db: DbSession
):
    """更新账号"""
    update_data = request.model_dump(exclude_unset=True)
    
    # 如果更新了Cookie，验证状态
    if "cookie_web_session" in update_data or "cookie_a1" in update_data:
        update_data["login_status"] = "valid"
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    account.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(account)
    
    return XHSAccountResponse.model_validate(account)


@router.delete("/{account_id}")
async def delete_account(
    account: XHSAccount = Depends(get_user_account),
    db: DbSession
):
    """删除账号"""
    await db.delete(account)
    await db.commit()
    
    return {"message": "删除成功"}


@router.post("/{account_id}/refresh-cookie")
async def refresh_account_cookie(
    request: dict,
    account: XHSAccount = Depends(get_user_account),
    db: DbSession
):
    """刷新账号Cookie"""
    cookie_web_session = request.get("cookie_web_session")
    cookie_a1 = request.get("cookie_a1")
    
    if not cookie_web_session or not cookie_a1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供完整的Cookie"
        )
    
    account.cookie_web_session = cookie_web_session
    account.cookie_a1 = cookie_a1
    account.login_status = "valid"
    account.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Cookie更新成功"}


@router.post("/bulk-delete")
async def bulk_delete_accounts(
    request: BulkDeleteRequest,
    current_user: CurrentUser,
    db: DbSession
):
    """批量删除账号"""
    result = await db.execute(
        select(XHSAccount).where(
            and_(
                XHSAccount.id.in_(request.ids),
                XHSAccount.user_id == current_user.id
            )
        )
    )
    accounts = result.scalars().all()
    
    for account in accounts:
        await db.delete(account)
    
    await db.commit()
    
    return {"message": f"已删除 {len(accounts)} 个账号"}


# ========== 规则接口 ==========

@router.get("/rules", response_model=List[ReplyRuleResponse])
async def get_rules(
    current_user: CurrentUser,
    db: DbSession,
    account_id: Optional[int] = None,
    rule_type: Optional[str] = None,
    is_enabled: Optional[bool] = None
):
    """获取规则列表"""
    query = select(ReplyRule).where(ReplyRule.user_id == current_user.id)
    
    if account_id:
        query = query.where(ReplyRule.account_id == account_id)
    if rule_type:
        query = query.where(ReplyRule.rule_type == rule_type)
    if is_enabled is not None:
        query = query.where(ReplyRule.is_enabled == is_enabled)
    
    query = query.order_by(ReplyRule.priority.desc(), ReplyRule.created_at.desc())
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return [ReplyRuleResponse.model_validate(r) for r in rules]


@router.post("/rules", response_model=ReplyRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    request: ReplyRuleCreate,
    current_user: CurrentUser,
    db: DbSession
):
    """创建规则"""
    # 检查规则数量限制
    if not current_user.check_limits("keywords"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="已达到规则数量上限，请升级套餐"
        )
    
    # 如果指定了账号，检查权限
    if request.account_id:
        result = await db.execute(
            select(XHSAccount).where(
                and_(
                    XHSAccount.id == request.account_id,
                    XHSAccount.user_id == current_user.id
                )
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号不存在或无权限"
            )
    
    rule = ReplyRule(
        user_id=current_user.id,
        account_id=request.account_id,
        name=request.name,
        rule_type=request.rule_type,
        match_type=request.match_type,
        keywords=request.keywords,
        reply_templates=request.reply_templates,
        priority=request.priority,
        is_enabled=request.is_enabled,
        use_ai_reply=request.use_ai_reply,
        ai_prompt=request.ai_prompt
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return ReplyRuleResponse.model_validate(rule)


@router.put("/rules/{rule_id}", response_model=ReplyRuleResponse)
async def update_rule(
    request: ReplyRuleUpdate,
    rule: ReplyRule = Depends(get_user_rule),
    db: DbSession
):
    """更新规则"""
    update_data = request.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    rule.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(rule)
    
    return ReplyRuleResponse.model_validate(rule)


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule: ReplyRule = Depends(get_user_rule),
    db: DbSession
):
    """删除规则"""
    await db.delete(rule)
    await db.commit()
    
    return {"message": "删除成功"}


@router.post("/rules/bulk-enable")
async def bulk_enable_rules(
    request: BulkEnableRequest,
    current_user: CurrentUser,
    db: DbSession
):
    """批量启用/禁用规则"""
    result = await db.execute(
        select(ReplyRule).where(
            and_(
                ReplyRule.id.in_(request.ids),
                ReplyRule.user_id == current_user.id
            )
        )
    )
    rules = result.scalars().all()
    
    for rule in rules:
        rule.is_enabled = request.enabled
        rule.updated_at = datetime.utcnow()
    
    await db.commit()
    
    status_text = "启用" if request.enabled else "禁用"
    return {"message": f"已{status_text} {len(rules)} 条规则"}


# ========== 统计接口 ==========

@router.get("/stats/overview", response_model=StatsOverview)
async def get_stats_overview(
    current_user: CurrentUser,
    db: DbSession
):
    """获取统计概览"""
    from app.models.db_models import ReplyHistory
    
    # 账号统计
    result = await db.execute(
        select(
            func.count(XHSAccount.id).label("total"),
            func.sum(func.cast(XHSAccount.is_active, int)).label("active")
        ).where(XHSAccount.user_id == current_user.id)
    )
    account_row = result.one()
    
    # 规则统计
    result = await db.execute(
        select(
            func.count(ReplyRule.id).label("total"),
            func.sum(func.cast(ReplyRule.is_enabled, int)).label("enabled")
        ).where(ReplyRule.user_id == current_user.id)
    )
    rule_row = result.one()
    
    # 回复统计
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(
            func.count(ReplyHistory.id).label("total"),
            func.sum(
                func.cast(ReplyHistory.reply_status == "success", int)
            ).label("success")
        ).where(
            and_(
                ReplyHistory.user_id == current_user.id,
                ReplyHistory.created_at >= today_start
            )
        )
    )
    reply_row = result.one()
    
    return StatsOverview(
        total_accounts=account_row.total or 0,
        active_accounts=account_row.active or 0,
        total_rules=rule_row.total or 0,
        enabled_rules=rule_row.enabled or 0,
        total_replies=current_user.total_replies,
        today_replies=current_user.today_replies,
        success_rate=round((reply_row.success or 0) / max(reply_row.total or 1, 1) * 100, 2)
    )


@router.get("/stats/trend", response_model=StatsTrendResponse)
async def get_stats_trend(
    current_user: CurrentUser,
    db: DbSession,
    period: str = Query("7d", pattern="^(7d|30d|90d)$")
):
    """获取趋势数据"""
    from app.models.db_models import ReplyHistory
    from datetime import timedelta
    
    days = {"7d": 7, "30d": 30, "90d": 90}[period]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 查询每日统计数据
    result = await db.execute(
        select(
            func.date(ReplyHistory.created_at).label("date"),
            func.count(ReplyHistory.id).label("replies"),
            func.sum(
                func.cast(ReplyHistory.reply_status == "success", int)
            ).label("success")
        ).where(
            and_(
                ReplyHistory.user_id == current_user.id,
                ReplyHistory.created_at >= start_date
            )
        ).group_by(
            func.date(ReplyHistory.created_at)
        ).order_by(
            func.date(ReplyHistory.created_at)
        )
    )
    rows = result.all()
    
    # 转换为数据点
    data = []
    for row in rows:
        data.append(TrendDataPoint(
            date=str(row.date),
            replies=row.replies,
            success=row.success or 0,
            failed=row.replies - (row.success or 0)
        ))
    
    return StatsTrendResponse(period=period, data=data)


@router.get("/history", response_model=ReplyHistoryListResponse)
async def get_reply_history(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    account_id: Optional[int] = None,
    target_type: Optional[str] = None,
    reply_status: Optional[str] = None
):
    """获取回复历史"""
    from app.models.db_models import ReplyHistory
    from sqlalchemy import and_
    
    query = select(ReplyHistory).where(ReplyHistory.user_id == current_user.id)
    
    if account_id:
        query = query.where(ReplyHistory.account_id == account_id)
    if target_type:
        query = query.where(ReplyHistory.target_type == target_type)
    if reply_status:
        query = query.where(ReplyHistory.reply_status == reply_status)
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 分页
    query = query.order_by(ReplyHistory.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    return ReplyHistoryListResponse(
        items=[ReplyHistoryResponse.model_validate(h) for h in history],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# 前向引用需要
from app.models.db_models import ReplyRule as ReplyRuleModel
from app.api.deps import get_user_rule as get_user_rule_dep
get_user_rule = get_user_rule_dep