"""
账号管理服务
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.db_models import XHSAccount


def create_account(
    db: Session,
    user_id: int,
    name: str,
    cookie_web_session: str = None,
    cookie_a1: str = None,
    monitor_comments: bool = True,
    monitor_messages: bool = False,
    monitor_note_ids: List[str] = None,
    ignored_users: List[str] = None
) -> XHSAccount:
    """创建账号"""
    account = XHSAccount(
        user_id=user_id,
        name=name,
        cookie_web_session=cookie_web_session,
        cookie_a1=cookie_a1,
        monitor_comments=monitor_comments,
        monitor_messages=monitor_messages,
        monitor_note_ids=monitor_note_ids or [],
        ignored_users=ignored_users or [],
        login_status="valid" if (cookie_web_session and cookie_a1) else "unknown"
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_accounts(db: Session, user_id: int, is_active: Optional[bool] = None) -> List[XHSAccount]:
    """获取用户账号列表"""
    query = db.query(XHSAccount).filter(XHSAccount.user_id == user_id)
    if is_active is not None:
        query = query.filter(XHSAccount.is_active == is_active)
    return query.all()


def get_account(db: Session, account_id: int, user_id: int) -> Optional[XHSAccount]:
    """获取账号详情"""
    return db.query(XHSAccount).filter(
        XHSAccount.id == account_id,
        XHSAccount.user_id == user_id
    ).first()


def update_account(
    db: Session,
    account: XHSAccount,
    name: str = None,
    cookie_web_session: str = None,
    cookie_a1: str = None,
    monitor_comments: bool = None,
    monitor_messages: bool = None,
    is_active: bool = None
) -> XHSAccount:
    """更新账号"""
    if name is not None:
        account.name = name
    if cookie_web_session is not None:
        account.cookie_web_session = cookie_web_session
    if cookie_a1 is not None:
        account.cookie_a1 = cookie_a1
    if cookie_web_session or cookie_a1:
        account.login_status = "valid"
    if monitor_comments is not None:
        account.monitor_comments = monitor_comments
    if monitor_messages is not None:
        account.monitor_messages = monitor_messages
    if is_active is not None:
        account.is_active = is_active
    
    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account: XHSAccount) -> None:
    """删除账号"""
    db.delete(account)
    db.commit()


def verify_cookie(account: XHSAccount) -> bool:
    """验证Cookie有效性（实际应调用小红书API）"""
    # 这里应该调用小红书API验证Cookie
    # 简化处理：如果Cookie存在则认为是有效的
    return bool(account.cookie_web_session and account.cookie_a1)