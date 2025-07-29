from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def _heart():
    """
    Health check endpoint.
    """
    return {"status": "running"}