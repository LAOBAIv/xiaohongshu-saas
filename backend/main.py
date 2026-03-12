from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import simple
from app.core.config import settings

app = FastAPI(
    title="小红书SAAS API",
    description="小红书自动回复多租户SAAS平台API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(simple.router, prefix="/api/v1", tags=["测试接口"])

@app.get("/api/v1/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
