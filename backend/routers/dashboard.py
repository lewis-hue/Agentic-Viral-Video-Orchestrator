from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DashboardData(BaseModel):
    trends: list
    videos_generated: int
    engagement_score: float
    optimization_suggestions: list

@router.get("/", response_model=DashboardData)
async def get_dashboard():
    # Placeholder data
    return {
        "trends": ["AI Tutorials", "Viral Challenges"],
        "videos_generated": 150,
        "engagement_score": 0.85,
        "optimization_suggestions": ["Increase hook length", "Use more trending music"]
    }