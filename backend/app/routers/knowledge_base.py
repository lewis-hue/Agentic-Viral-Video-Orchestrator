from fastapi import APIRouter
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()
kb_service = KnowledgeBaseService()

@router.get("/tips")
async def get_all_tips():
    return kb_service.get_all_tips()

@router.get("/tips/{category}")
async def get_tips_by_category(category: str):
    return kb_service.get_tips_by_category(category)

@router.get("/tip/{tip_id}")
async def get_tip_by_id(tip_id: int):
    tip = kb_service.get_tip_by_id(tip_id)
    if not tip:
        return {"error": "Tip not found"}
    return tip