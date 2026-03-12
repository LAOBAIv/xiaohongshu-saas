"""
小红书爬虫服务
"""
import re
import time
import json
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


class XHSCrawler:
    """小红书爬虫"""
    
    def __init__(self, cookie_a1: str = None, cookie_web_session: str = None):
        self.cookie_a1 = cookie_a1
        self.cookie_web_session = cookie_web_session
        self.headers = {
            "User-Agent": ua.random,
            "Referer": "https://www.xiaohongshu.com/",
            "Origin": "https://www.xiaohongshu.com"
        }
        self.session = requests.Session()
        self._update_cookies()
    
    def _update_cookies(self):
        """更新Cookie"""
        cookies = {}
        if self.cookie_a1:
            cookies["a1"] = self.cookie_a1
        if self.cookie_web_session:
            cookies["web_session"] = self.cookie_web_session
        self.session.cookies.update(cookies)
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        url = f"https://edith.xiaohongshu.com/api/sns/web/v1/user/otherinfo?target_user_id={user_id}"
        
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            data = resp.json()
            
            if data.get("success"):
                return data.get("data", {})
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def get_notes_by_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的笔记"""
        url = "https://edith.xiaohongshu.com/api/sns/web/v1/notes"
        
        payload = {
            "target_user_id": user_id,
            "cursor": "",
            "limit": limit
        }
        
        try:
            resp = self.session.post(url, json=payload, headers=self.headers, timeout=10)
            data = resp.json()
            
            if data.get("success"):
                return data.get("data", {}).get("notes", [])
            return []
        except Exception as e:
            print(f"获取笔记失败: {e}")
            return []
    
    def get_note_comments(self, note_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取笔记的评论"""
        url = f"https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor=&top_comment_id=&limit={limit}"
        
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            data = resp.json()
            
            if data.get("success"):
                comments = data.get("data", {}).get("comments", [])
                # 提取评论信息
                result = []
                for c in comments:
                    result.append({
                        "comment_id": c.get("comment_id"),
                        "user_id": c.get("user", {}).get("user_id"),
                        "nickname": c.get("user", {}).get("nickname"),
                        "content": c.get("content"),
                        "create_time": c.get("create_time"),
                        "like_count": c.get("like_count", 0)
                    })
                return result
            return []
        except Exception as e:
            print(f"获取评论失败: {e}")
            return []
    
    def get_note_detail(self, note_id: str) -> Optional[Dict[str, Any]]:
        """获取笔记详情"""
        url = f"https://edith.xiaohongshu.com/api/sns/web/v1/notes/{note_id}"
        
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            data = resp.json()
            
            if data.get("success"):
                note = data.get("data", {}).get("note", {})
                return {
                    "note_id": note.get("note_id"),
                    "title": note.get("title"),
                    "desc": note.get("desc"),
                    "type": note.get("type"),
                    "user": note.get("user", {}).get("nickname"),
                    "like_count": note.get("liked_count", 0),
                    "collect_count": note.get("collected_count", 0),
                    "comment_count": note.get("comment_count", 0)
                }
            return None
        except Exception as e:
            print(f"获取笔记详情失败: {e}")
            return None
    
    def post_comment(self, note_id: str, content: str) -> bool:
        """发表评论"""
        url = "https://edith.xiaohongshu.com/api/sns/web/v1/comment"
        
        payload = {
            "note_id": note_id,
            "content": content,
            "at_users": []
        }
        
        try:
            resp = self.session.post(url, json=payload, headers=self.headers, timeout=10)
            data = resp.json()
            return data.get("success", False)
        except Exception as e:
            print(f"发表评论失败: {e}")
            return False
    
    def send_message(self, user_id: str, content: str) -> bool:
        """发送私信"""
        url = "https://edith.xiaohongshu.com/api/sns/web/v1/im/chatmsgs"
        
        payload = {
            "target_user_id": user_id,
            "content": json.dumps({"type": 1, "content": content})
        }
        
        try:
            resp = self.session.post(url, json=payload, headers=self.headers, timeout=10)
            data = resp.json()
            return data.get("success", False)
        except Exception as e:
            print(f"发送私信失败: {e}")
            return False


def monitor_account(
    account,
    db,
    callback=None
) -> List[Dict[str, Any]]:
    """
    监控账号新评论
    callback: 回调函数，用于处理新评论
    """
    crawler = XHSCrawler(
        cookie_a1=account.cookie_a1,
        cookie_web_session=account.cookie_web_session
    )
    
    new_comments = []
    
    # 如果配置了监控特定笔记
    if account.monitor_note_ids:
        for note_id in account.monitor_note_ids:
            comments = crawler.get_note_comments(note_id)
            for c in comments:
                c["note_id"] = note_id
                new_comments.append(c)
    else:
        # 获取用户所有笔记的评论
        # 实际应该存储上次的检查位置，这里简化处理
        pass
    
    # 调用回调处理评论
    if callback and new_comments:
        for comment in new_comments:
            callback(comment, account, db)
    
    return new_comments


def auto_reply_comment(
    crawler: XHSCrawler,
    comment: Dict[str, Any],
    rules: List,
    db
) -> bool:
    """
    自动回复评论
    """
    content = comment.get("content", "")
    
    # 匹配规则
    matched_rule = None
    for rule in rules:
        if rule.rule_type == "random":
            matched_rule = rule
            break
        
        if not rule.keywords:
            continue
        
        for keyword in rule.keywords:
            if rule.match_type == "exact" and keyword == content:
                matched_rule = rule
                break
            elif rule.match_type == "fuzzy" and keyword in content:
                matched_rule = rule
                break
            
            if matched_rule:
                break
    
    if not matched_rule:
        return False
    
    # 生成回复内容
    reply_content = matched_rule.reply_content
    
    if matched_rule.rule_type == "ai":
        # TODO: 调用AI生成回复
        pass
    
    # 延迟回复
    if matched_rule.reply_delay > 0:
        time.sleep(matched_rule.reply_delay)
    
    # 发送回复
    success = crawler.post_comment(comment.get("note_id"), reply_content)
    
    return success