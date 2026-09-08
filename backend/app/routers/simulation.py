from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_simulation():
    return {"simulation": "Simulation results"}