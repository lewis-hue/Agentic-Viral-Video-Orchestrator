from fastapi import APIRouter
from pydantic import BaseModel
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()
kb_service = KnowledgeBaseService()

class CriticismRequest(BaseModel):
    content: str
    voice_input: str = None
    attached_files: list[str] = []

@router.post("/")
async def criticize_content(request: CriticismRequest):
    # Use knowledge base to generate criticism
    tips = kb_service.get_all_tips()
    criticism_points = []
    for tip in tips[:3]:  # Use first 3 tips
        criticism_points.append(f"Based on '{tip.tip}': {tip.description}")
    additional_context = ""
    if request.voice_input:
        additional_context += f" Voice input: {request.voice_input}"
    if request.attached_files:
        additional_context += f" Attached files: {', '.join(request.attached_files)}"
    return {"criticism": " ".join(criticism_points) + additional_context}