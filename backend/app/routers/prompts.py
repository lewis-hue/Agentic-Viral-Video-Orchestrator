from fastapi import APIRouter
from pydantic import BaseModel
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()
kb_service = KnowledgeBaseService()

class PromptRequest(BaseModel):
    topic: str
    voice_input: str = None
    attached_files: list[str] = []

class EditPromptRequest(BaseModel):
    topic: str
    updated_prompt: str
    voice_input: str = None
    attached_files: list[str] = []

@router.post("/generate")
async def generate_prompt(request: PromptRequest):
    # Use knowledge base to generate prompt
    tips = kb_service.get_all_tips()
    criteria = [tip.tip for tip in tips[:3]]
    additional_context = ""
    if request.voice_input:
        additional_context += f" Voice input: {request.voice_input}"
    if request.attached_files:
        additional_context += f" Attached files: {', '.join(request.attached_files)}"
    prompt = {
        "prompt": f"Create a viral video about {request.topic} incorporating: {', '.join(criteria)}.{additional_context}",
        "criteria": criteria
    }
    return prompt

@router.post("/edit")
async def edit_prompt(request: EditPromptRequest):
    # Placeholder for editing
    additional_context = ""
    if request.voice_input:
        additional_context += f" Voice input: {request.voice_input}"
    if request.attached_files:
        additional_context += f" Attached files: {', '.join(request.attached_files)}"
    return {"updated_prompt": f"{request.updated_prompt}{additional_context}"}