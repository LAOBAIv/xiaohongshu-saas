"""
简易API接口，用于测试
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["简易测试"])

# 数据模型
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    token: str

# 模拟数据库
fake_users = [
    {"id": 1, "username": "admin", "password": "123456", "email": "admin@example.com"}
]
next_user_id = 2

# 模拟Token
fake_tokens = {
    "test-token-123": 1
}

@router.post("/login", response_model=UserInfo)
async def login(request: UserLogin):
    """登录接口"""
    for user in fake_users:
        if user["username"] == request.username and user["password"] == request.password:
            token = f"token-{user['id']}-{hash(request.username)}"
            fake_tokens[token] = user["id"]
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "token": token
            }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误"
    )

@router.post("/register", response_model=UserInfo)
async def register(request: UserRegister):
    """注册接口"""
    global next_user_id
    
    # 检查用户名是否存在
    for user in fake_users:
        if user["username"] == request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    new_user = {
        "id": next_user_id,
        "username": request.username,
        "password": request.password,
        "email": request.email
    }
    fake_users.append(new_user)
    next_user_id += 1
    
    token = f"token-{new_user['id']}-{hash(request.username)}"
    fake_tokens[token] = new_user["id"]
    
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "token": token
    }

@router.get("/profile")
async def get_profile(token: str):
    """获取用户信息"""
    if token not in fake_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效"
        )
    
    user_id = fake_tokens[token]
    for user in fake_users:
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="用户不存在"
    )
