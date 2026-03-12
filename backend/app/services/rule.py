"""
规则管理服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_models import ReplyRule, XHSAccount


def create_rule(
    db: Session,
    user_id: int,
    name: str,
    rule_type: str,
    reply_content: str,
    account_id: int = None,
    keywords: List[str] = None,
    ai_prompt: str = None,
    match_type: str = "exact",
    priority: int = 0,
    is_enabled: bool = True,
    reply_delay: int = 0
) -> ReplyRule:
    """创建规则"""
    rule = ReplyRule(
        user_id=user_id,
        account_id=account_id,
        name=name,
        rule_type=rule_type,
        keywords=keywords or [],
        reply_content=reply_content,
        ai_prompt=ai_prompt,
        match_type=match_type,
        priority=priority,
        is_enabled=is_enabled,
        reply_delay=reply_delay
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_rules(
    db: Session,
    user_id: int,
    account_id: int = None,
    rule_type: str = None,
    is_enabled: bool = None
) -> List[ReplyRule]:
    """获取规则列表"""
    query = db.query(ReplyRule).filter(ReplyRule.user_id == user_id)
    
    if account_id:
        query = query.filter(ReplyRule.account_id == account_id)
    if rule_type:
        query = query.filter(ReplyRule.rule_type == rule_type)
    if is_enabled is not None:
        query = query.filter(ReplyRule.is_enabled == is_enabled)
    
    return query.order_by(ReplyRule.priority.desc(), ReplyRule.created_at.desc()).all()


def get_rule(db: Session, rule_id: int, user_id: int) -> Optional[ReplyRule]:
    """获取规则详情"""
    return db.query(ReplyRule).filter(
        ReplyRule.id == rule_id,
        ReplyRule.user_id == user_id
    ).first()


def update_rule(
    db: Session,
    rule: ReplyRule,
    name: str = None,
    reply_content: str = None,
    keywords: List[str] = None,
    ai_prompt: str = None,
    match_type: str = None,
    priority: int = None,
    is_enabled: bool = None,
    reply_delay: int = None
) -> ReplyRule:
    """更新规则"""
    if name is not None:
        rule.name = name
    if reply_content is not None:
        rule.reply_content = reply_content
    if keywords is not None:
        rule.keywords = keywords
    if ai_prompt is not None:
        rule.ai_prompt = ai_prompt
    if match_type is not None:
        rule.match_type = match_type
    if priority is not None:
        rule.priority = priority
    if is_enabled is not None:
        rule.is_enabled = is_enabled
    if reply_delay is not None:
        rule.reply_delay = reply_delay
    
    rule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule: ReplyRule) -> None:
    """删除规则"""
    db.delete(rule)
    db.commit()


def match_rule(content: str, rule: ReplyRule) -> bool:
    """匹配规则"""
    if not rule.is_enabled:
        return False
    
    if rule.rule_type == "random":
        return True
    
    if not rule.keywords:
        return False
    
    if rule.match_type == "exact":
        return any(kw == content for kw in rule.keywords)
    elif rule.match_type == "fuzzy":
        return any(kw in content for kw in rule.keywords)
    elif rule.match_type == "regex":
        import re
        return any(re.search(kw, content) for kw in rule.keywords)
    
    return False