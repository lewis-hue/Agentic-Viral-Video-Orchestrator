from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ReviewData(BaseModel):
    script_id: str
    approved: bool
    feedback: str

@router.post("/review")
async def human_review(data: ReviewData):
    # Placeholder for human review
    if data.approved:
        return {"status": "Approved", "next_step": "Generate video"}
    else:
        return {"status": "Rejected", "feedback": data.feedback}