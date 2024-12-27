from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/api")
async def api_health_check() -> dict[str, str]:
    return {"status": "healthy"}