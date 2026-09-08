from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_dashboard_data():
    # Placeholder data
    return {
        "trends": ["TikTok Challenges", "Short Tutorials"],
        "videos_generated": 10,
        "engagement_score": 85,
        "optimization_suggestions": ["Use more trending sounds", "Shorten video length"]
    }