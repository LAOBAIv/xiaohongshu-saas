"""
统计服务
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.db_models import XHSAccount, ReplyRule, ReplyHistory


def get_account_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """获取账号统计"""
    result = db.query(
        func.count(XHSAccount.id).label("total"),
        func.sum(func.cast(XHSAccount.is_active, int)).label("active")
    ).filter(XHSAccount.user_id == user_id).first()
    
    return {
        "total": result.total or 0,
        "active": result.active or 0
    }


def get_rule_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """获取规则统计"""
    result = db.query(
        func.count(ReplyRule.id).label("total"),
        func.sum(func.cast(ReplyRule.is_enabled, int)).label("enabled"),
        func.sum(ReplyRule.match_count).label("total_matches"),
        func.sum(ReplyRule.reply_count).label("total_replies")
    ).filter(ReplyRule.user_id == user_id).first()
    
    return {
        "total": result.total or 0,
        "enabled": result.enabled or 0,
        "total_matches": result.total_matches or 0,
        "total_replies": result.total_replies or 0
    }


def get_reply_history(
    db: Session,
    user_id: int,
    account_id: int = None,
    limit: int = 50
) -> List[ReplyHistory]:
    """获取回复历史"""
    query = db.query(ReplyHistory).join(
        XHSAccount, ReplyHistory.account_id == XHSAccount.id
    ).filter(XHSAccount.user_id == user_id)
    
    if account_id:
        query = query.filter(ReplyHistory.account_id == account_id)
    
    return query.order_by(ReplyHistory.created_at.desc()).limit(limit).all()


def get_stats_overview(db: Session, user_id: int) -> Dict[str, Any]:
    """获取统计概览"""
    # 账号统计
    account_stats = get_account_stats(db, user_id)
    
    # 规则统计
    rule_stats = get_rule_stats(db, user_id)
    
    # 今日回复数
    today = datetime.utcnow().date()
    today_replies = db.query(func.count(ReplyHistory.id)).join(
        XHSAccount, ReplyHistory.account_id == XHSAccount.id
    ).filter(
        and_(
            XHSAccount.user_id == user_id,
            func.date(ReplyHistory.created_at) == today
        )
    ).scalar() or 0
    
    return {
        "accounts": account_stats,
        "rules": rule_stats,
        "today_replies": today_replies
    }


def get_stats_trend(
    db: Session,
    user_id: int,
    days: int = 7
) -> List[Dict[str, Any]]:
    """获取趋势数据"""
    trends = []
    
    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=i)
        
        # 统计当日的回复数
        count = db.query(func.count(ReplyHistory.id)).join(
            XHSAccount, ReplyHistory.account_id == XHSAccount.id
        ).filter(
            and_(
                XHSAccount.user_id == user_id,
                func.date(ReplyHistory.created_at) == date
            )
        ).scalar() or 0
        
        trends.append({
            "date": date.isoformat(),
            "count": count
        })
    
    return list(reversed(trends))


def record_reply(
    db: Session,
    account_id: int,
    rule_id: int,
    comment_id: str,
    note_id: str,
    user_id: str,
    username: str,
    content: str,
    reply_content: str,
    status: str = "success",
    error_message: str = None
) -> ReplyHistory:
    """记录回复"""
    history = ReplyHistory(
        account_id=account_id,
        rule_id=rule_id,
        comment_id=comment_id,
        note_id=note_id,
        user_id=user_id,
        username=username,
        content=content,
        reply_content=reply_content,
        reply_status=status,
        reply_at=datetime.utcnow() if status == "success" else None,
        error_message=error_message
    )
    db.add(history)
    
    # 更新规则统计
    rule = db.query(ReplyRule).filter(ReplyRule.id == rule_id).first()
    if rule:
        rule.match_count += 1
        if status == "success":
            rule.reply_count += 1
    
    db.commit()
    db.refresh(history)
    return history