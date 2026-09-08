from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_review():
    return {"review": "Performance review data"}